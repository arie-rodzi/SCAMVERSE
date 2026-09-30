"""Unit tests for the SCAMVERSE analysis engine (no Streamlit required)."""
import pytest

from modules.engine import (
    RISK_RULES,
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
    assert active_indicators(a) == int((rdf["Detected Evidence"] > 0).sum())
    assert abs(tdf["Relative Weight"].sum() - 1) < 0.01
    words = len(SAMPLE.split())
    for _, r in rdf.iterrows():
        assert r["Index Contribution"] == min(r["Detected Evidence"], 5)
        assert r["Per 1,000 Words"] == round(r["Detected Evidence"] * 1000 / words, 2)
    # Every coded extract must come from the source text.
    for extract in codes_df(a)["Evidence Extract"]:
        assert extract in SAMPLE
