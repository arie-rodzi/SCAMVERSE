"""Unit tests for the SCAMVERSE analysis engine (no Streamlit required)."""
import pytest

import json

from modules.engine import (
    count_terms,
    RISK_RULES,
    default_lexicon,
    load_lexicon,
    prepare_text,
    THEME_KEYWORDS,
    active_dimensions,
    active_indicators,
    analyze_text,
    codes_df,
    count_term,
    risk_df,
    theme_df,
)

SAMPLE = (
    "The victim joined a Telegram group after seeing Facebook ads. "
    "The scammer promised a guaranteed profit and a 30% return within days. "
    "Money was transferred to a mule account at another bank. "
    "The victim lodged a police report and PDRM started an investigation."
)


# --- whole-term matching -------------------------------------------------------

@pytest.mark.parametrize(
    "term, text, expected",
    [
        ("sc", "scam scammer scams describe", 0),   # acronym must not match inside words
        ("sc", "reported to the sc and bnm", 1),
        ("tac", "please contact the attacker", 0),
        ("tac", "he shared his tac number", 1),
        ("layer", "the player lost", 0),
        ("victim", "two victims and one victim", 2),  # plural accepted
        ("account", "mule accounts", 1),
        ("30%", "a 30% return", 1),
        ("30%", "a 300% return", 0),
        ("social media", "via social media groups", 1),
        ("guarantee", "a guaranteed return", 1),          # inflectional suffix accepted
        ("arrest", "suspects were arrested", 1),
        ("layer", "layering of funds", 1),
    ],
)
def test_count_term_whole_word(term, text, expected):
    assert count_term(term, text) == expected


# --- analysis object -----------------------------------------------------------

def test_analysis_keys_and_shapes():
    a = analyze_text(SAMPLE)
    for key in ("text", "theme_counts", "evidence", "risk_hits", "risk_score",
                "risk_level", "top_terms", "codes"):
        assert key in a
    assert set(a["theme_counts"]) == set(THEME_KEYWORDS)
    assert set(a["risk_hits"]) == set(RISK_RULES)


def test_deterministic():
    assert analyze_text(SAMPLE) == analyze_text(SAMPLE)


def test_risk_score_bounded_and_banded():
    heavy = " ".join(["guaranteed profit high return urgent telegram mule account crypto "
                      "testimonial unlicensed"] * 50)
    for text in ("", SAMPLE, heavy):
        a = analyze_text(text)
        assert 0 <= a["risk_score"] <= 100
        expected = "High" if a["risk_score"] >= 70 else "Moderate" if a["risk_score"] >= 35 else "Low"
        assert a["risk_level"] == expected
    assert analyze_text(heavy)["risk_score"] == 100


def test_per_rule_cap():
    # One rule hit many times cannot exceed its cap of 5 of the 5*|R| maximum.
    a = analyze_text("telegram " * 100)
    assert a["risk_score"] == int(5 / (len(RISK_RULES) * 5) * 100)


def test_evidence_limited_to_five_per_dimension():
    text = " ".join(f"The victim number {i} lost money to the scheme." for i in range(20))
    a = analyze_text(text)
    for extracts in a["evidence"].values():
        assert len(extracts) <= 5


def test_empty_input():
    a = analyze_text("")
    assert a["risk_score"] == 0 and a["risk_level"] == "Low"
    assert active_dimensions(a) == 0 and active_indicators(a) == 0
    assert list(codes_df(a).columns) == ["Dimension", "Indicative Code", "Evidence Extract"]


def test_active_counts_and_frames():
    a = analyze_text(SAMPLE)
    tdf, rdf = theme_df(a), risk_df(a)
    assert active_dimensions(a) == int((tdf["Evidence Frequency"] > 0).sum())
    assert active_indicators(a) == int((rdf["Matches"] > 0).sum())
    assert abs(tdf["Relative Weight"].sum() - 1) < 0.01
    words = len(SAMPLE.split())
    for _, r in rdf.iterrows():
        assert r["Index Contribution"] == min(r["Matches"], 5)
        assert r["Per 1,000 Words"] == round(r["Matches"] * 1000 / words, 2)
    # Every coded extract must come from the source text.
    for extract in codes_df(a)["Evidence Extract"]:
        assert extract in SAMPLE


# --- normalisation, speaker turns, lexicons, provenance -------------------------

def test_line_breaks_do_not_split_multiword_terms():
    # regression: counts and evidence must use the same normalised text
    a = analyze_text("Victims were recruited through social\nmedia groups every single day.")
    assert count_term("social media", "social media") == 1
    assert a["theme_counts"]["Digital Recruitment Infrastructure"] >= 2   # social media + group
    assert active_dimensions(a) >= 1 and len(a["codes"]) >= 1


def test_prepare_text_removes_interviewer_turns_and_labels():
    raw = ("Interviewer: What do the offenders promise?\n"
           "Officer A: A guaranteed return.\n"
           "They also send receipts.\n\n"
           "Interviewer: Anything else?\nNot really.\n")
    out = prepare_text(raw)
    assert "promise" not in out and "Officer A:" not in out
    assert "A guaranteed return." in out and "They also send receipts." in out
    kept = prepare_text(raw, strip_labels=False, exclude_speakers=())
    assert "Interviewer: What do the offenders promise?" in kept and "Officer A:" in kept


def test_custom_lexicon_and_hashes():
    lex = load_lexicon(json.dumps({"dimensions": {"Only": ["telegram"]}, "indicators": {"Ind": ["profit"]}}))
    a = analyze_text("Telegram groups promised profit and more profit.", lex)
    assert a["theme_counts"] == {"Only": 1} and a["risk_hits"] == {"Ind": 2}
    assert a["risk_score"] == int(2 / 5 * 100) and a["lexicon_name"] == "custom"
    b = analyze_text("Telegram groups promised profit and more profit.")
    assert a["corpus_sha256"] == b["corpus_sha256"] and a["lexicon_sha256"] != b["lexicon_sha256"]
    assert b["lexicon_sha256"] == analyze_text("x", default_lexicon())["lexicon_sha256"]


def test_load_lexicon_rejects_bad_input():
    with pytest.raises(ValueError):
        load_lexicon(json.dumps({"dimensions": {}, "indicators": {"a": ["b"]}}))
    with pytest.raises(ValueError):
        load_lexicon(json.dumps({"dimensions": {"a": []}, "indicators": {"a": ["b"]}}))


def test_acronym_codes_are_upper_case():
    a = analyze_text("The report was lodged with PDRM and SSM on the same day.")
    assert {"PDRM", "SSM"} & set(codes_df(a)["Indicative Code"])


def test_overlapping_terms_count_once():
    assert count_terms(["high return", "return"], "a high return and a return") == 2
    assert count_terms(["guarantee", "guaranteed"], "guaranteed profit") == 1
    assert count_terms(["mule", "account"], "mule account") == 2   # adjacent, not overlapping
