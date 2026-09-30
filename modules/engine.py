import hashlib
import json
import re
from collections import Counter, defaultdict
import pandas as pd

THEME_KEYWORDS = {
    "Digital Recruitment Infrastructure": ["telegram", "facebook", "whatsapp", "wechat", "social media", "group", "link", "ads", "online", "platform"],
    "Psychological Manipulation & Legitimacy Cues": ["guarantee", "profit", "return", "dividend", "testimonial", "receipt", "urgent", "bonus", "promise", "trust"],
    "Victim Vulnerability & Decision Behaviour": ["victim", "retiree", "teacher", "student", "professional", "nurse", "lecturer", "greed", "young", "older", "salary"],
    "Scammer Operational Architecture": ["syndicate", "mastermind", "call center", "agent", "script", "fake", "company", "seminar", "package", "slot"],
    "Financial Transaction & Laundering Chain": ["bank", "account", "mule", "atm", "transfer", "transferred", "tac", "crypto", "wallet", "money", "layer"],
    "Institutional Response & Enforcement": ["police", "pdrm", "bnm", "bank negara", "ssm", "skmm", "sc", "nsrc", "bukit aman", "ipk", "ipd", "section 420"],
    "Evidence, Investigation & Prosecution": ["evidence", "receipt", "report", "statement", "investigation", "court", "arrest", "dpp", "nfa", "charge"],
    "Prevention, Awareness & Public Resilience": ["awareness", "campaign", "education", "prevent", "prevention", "hotline", "mule check", "alert", "seminar", "tips"],
}

RISK_RULES = {
    "Unrealistic high return": ["high return", "30%", "300%", "profit", "return", "dividend", "bonus", "rm50,000", "million"],
    "Guaranteed profit or no-risk claim": ["guarantee", "guaranteed", "confirm", "no risk", "risk-free", "sure profit"],
    "Telegram or social media recruitment": ["telegram", "facebook", "whatsapp", "wechat", "social media", "link"],
    "Mule account or layered transfer": ["mule", "account", "atm", "transfer", "transferred", "bank", "layer", "money out"],
    "Fake testimonial or fabricated proof": ["testimonial", "receipt", "screenshot", "proof", "dividend received", "got my profit"],
    "Unlicensed or unclear investment entity": ["no license", "unlicensed", "ssm", "bank negara", "bnm", "not listed", "company"],
    "Crypto or cross-border laundering": ["crypto", "cryptocurrency", "bitcoin", "overseas", "out of the country", "foreign"],
    "Urgency pressure": ["urgent", "immediate", "short period", "limited", "act now", "within 3 hours"],
}

RISK_CAP = 5  # maximum hits per indicator that count towards the bounded index

STAKEHOLDERS = {
    "PDRM / CCID": "Investigation, evidence gathering, arrest, prosecution support, public warnings and inter-agency coordination.",
    "BNM": "Financial licensing, financial consumer alert list, transaction-monitoring guidance and banking coordination.",
    "Banks": "Real-time suspicious transaction monitoring, mule-account detection, account freezing and victim response.",
    "SSM": "Company registration verification, fraud-risk flagging and entity legitimacy checks.",
    "SKMM / Telcos": "SIM-card governance, scam-number monitoring and platform-level digital enforcement support.",
    "NSRC": "Rapid scam reporting, transaction blocking coordination and victim response support.",
    "Social Media Platforms": "Scam advertisement takedown, suspicious group monitoring and fake testimonial detection.",
    "Public / Victims": "Due diligence, financial literacy, scam reporting and account protection.",
}

STOPWORDS = set("""this that with from they them were have been will into when what where which there their about because under above after before also only most more some such case cases scam scams scammer scammers victim victims police investment investments online money account bank report reports investigation commercial section fraud fraudulent people person another through between however usually actually maybe every many much none very then than also here there current related against among these those into does done did not are was has had can could should would our your his her him she him itself ourselves themselves""".split())

_PATTERN_CACHE = {}

# Inflectional endings accepted after a lexicon term, so that "victim" matches
# "victims", "guarantee" matches "guaranteed" and "arrest" matches "arrested".
SUFFIXES = r"(?:s|es|d|ed|ing)?"

# Terms shown in upper case in the code table (acronyms).
ACRONYMS = {"pdrm", "bnm", "ssm", "skmm", "sc", "nsrc", "ipk", "ipd", "atm", "tac", "dpp", "nfa"}


def _pattern(term: str):
    """Case-insensitive whole-term pattern with an optional inflectional suffix.

    Terms match only when not embedded in a longer word, so the agency acronym
    "sc" does not match "scam" and "tac" does not match "contact". Look-arounds
    are used instead of \b so that terms ending in non-word characters (e.g.
    "30%") are handled correctly.
    """
    pat = _PATTERN_CACHE.get(term)
    if pat is None:
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(term.lower()) + SUFFIXES + r"(?![A-Za-z0-9])")
        _PATTERN_CACHE[term] = pat
    return pat


def count_term(term: str, lower_text: str) -> int:
    """Number of whole-term occurrences of `term` in already-lowercased text."""
    return len(_pattern(term).findall(lower_text))


def count_terms(terms, lower_text: str) -> int:
    """Occurrences of any term of a list, counting each stretch of text once.

    Overlapping matches (e.g. "high return" and "return", or "guarantee" and
    "guaranteed" at the same position) are merged, so one occurrence in the text
    adds one to a dimension or indicator however many of its terms it matches.
    """
    spans = sorted(m.span() for t in terms for m in _pattern(t).finditer(lower_text))
    count, end = 0, -1
    for a, b in spans:
        if a >= end:
            count += 1
            end = b
        else:
            end = max(end, b)
    return count


def has_term(term: str, lower_text: str) -> bool:
    return _pattern(term).search(lower_text) is not None


def clean_text(text: str) -> str:
    """Collapse all runs of white space (including line breaks) to single spaces."""
    return re.sub(r"\s+", " ", text or "").strip()


def split_sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text(text)) if len(s.strip()) > 20]


# ----------------------------------------------------------------------------- speaker turns

_LABEL = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 .'\-]{0,30}?)\s*:\s+(.*)$")


def prepare_text(text: str, strip_labels: bool = True, exclude_speakers=("interviewer",)) -> str:
    """Pre-process an interview transcript before analysis.

    A line of the form ``Label: utterance`` starts a speaker turn that runs until
    the next labelled line. Turns whose label starts with any entry of
    ``exclude_speakers`` (case-insensitive) are removed, and the ``Label:`` prefix
    is removed from the remaining turns when ``strip_labels`` is true, so that
    interviewer questions and speaker names are not coded or counted.
    Lines without a label are kept unchanged.
    """
    excluded = tuple(x.strip().lower() for x in (exclude_speakers or ()) if x.strip())
    out, skipping = [], False
    for line in (text or "").splitlines():
        m = _LABEL.match(line)
        if m:
            label, rest = m.group(1).strip().lower(), m.group(2)
            skipping = bool(excluded) and label.startswith(excluded)
            if skipping:
                continue
            out.append(rest if strip_labels else line)
        elif not skipping or not line.strip():
            if not line.strip():
                skipping = False
            out.append(line)
    return "\n".join(out)


# ----------------------------------------------------------------------------- lexicons

def default_lexicon() -> dict:
    return {"dimensions": THEME_KEYWORDS, "indicators": RISK_RULES}


def load_lexicon(raw: str) -> dict:
    """Parse a lexicon JSON document: {"dimensions": {name: [terms]}, "indicators": {name: [terms]}}."""
    data = json.loads(raw)
    lex = {}
    for key in ("dimensions", "indicators"):
        block = data.get(key)
        if not isinstance(block, dict) or not block:
            raise ValueError(f"lexicon must contain a non-empty '{key}' object")
        lex[key] = {str(k): [str(t).strip().lower() for t in v if str(t).strip()] for k, v in block.items()}
        if any(not terms for terms in lex[key].values()):
            raise ValueError(f"every entry in '{key}' needs at least one term")
    return lex


def _sha256(obj) -> str:
    data = obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- analysis

def analyze_text(text: str, lexicon: dict = None):
    """Analyse a corpus. Deterministic: the same text and lexicon give the same result."""
    text = text or ""
    lex = lexicon or default_lexicon()
    dims, rules = lex["dimensions"], lex["indicators"]
    lower = clean_text(text).lower()          # counts and evidence use the same normalised text
    sentences = split_sentences(text)
    theme_counts = {}
    evidence = defaultdict(list)
    codes = []
    for theme, keys in dims.items():
        theme_counts[theme] = count_terms(keys, lower)
        for sent in sentences:
            s_lower = sent.lower()
            hit_keys = [k for k in keys if has_term(k, s_lower)]
            if hit_keys:
                term = hit_keys[0]
                evidence[theme].append(sent[:420])
                codes.append({"Dimension": theme,
                              "Indicative Code": term.upper() if term in ACRONYMS else term.capitalize(),
                              "Evidence Extract": sent[:360]})
                if len(evidence[theme]) >= 5:
                    break
    risk_hits = {rule: count_terms(keys, lower) for rule, keys in rules.items()}
    raw_score = sum(min(v, RISK_CAP) for v in risk_hits.values())
    risk_score = int(raw_score / (len(rules) * RISK_CAP) * 100)
    risk_level = "High" if risk_score >= 70 else "Moderate" if risk_score >= 35 else "Low"
    words = re.findall(r"[A-Za-z]{4,}", lower)
    top_terms = Counter([w for w in words if w not in STOPWORDS]).most_common(30)
    return {"text": text, "theme_counts": theme_counts, "evidence": dict(evidence), "risk_hits": risk_hits,
            "risk_score": risk_score, "risk_level": risk_level, "top_terms": top_terms, "codes": codes,
            "lexicon_sha256": _sha256(lex), "corpus_sha256": _sha256(text),
            "lexicon_name": "default" if lexicon is None else "custom"}


def active_dimensions(analysis) -> int:
    """Number of ecosystem dimensions with at least one lexicon match."""
    return sum(1 for v in analysis["theme_counts"].values() if v > 0)


def active_indicators(analysis) -> int:
    """Number of warning indicators with at least one lexicon match."""
    return sum(1 for v in analysis["risk_hits"].values() if v > 0)


def theme_df(analysis):
    counts = analysis["theme_counts"]
    total = sum(counts.values()) or 1
    df = pd.DataFrame({"Dimension": list(counts.keys()), "Evidence Frequency": list(counts.values()),
                       "Relative Weight": [round(v / total, 3) for v in counts.values()]})
    # stable sort: ties keep lexicon order
    return df.sort_values("Evidence Frequency", ascending=False, kind="stable")


def word_count(text: str) -> int:
    return len((text or "").split())


def risk_df(analysis):
    """Per-indicator matches, capped contribution to the index, and density per 1,000 words.

    The density column is independent of the cap, so indicators remain comparable
    across corpora of different sizes even when the bounded index saturates.
    """
    hits = analysis["risk_hits"]
    words = max(word_count(analysis.get("text", "")), 1)
    return pd.DataFrame({
        "Warning Indicator": list(hits.keys()),
        "Matches": list(hits.values()),
        "Index Contribution": [min(v, RISK_CAP) for v in hits.values()],
        "Per 1,000 Words": [round(v * 1000 / words, 2) for v in hits.values()],
        "Interpretation": ["Strong signal" if v >= 3 else "Present" if v > 0 else "Not detected" for v in hits.values()],
    })


def codes_df(analysis):
    df = pd.DataFrame(analysis.get("codes", []))
    if df.empty:
        return pd.DataFrame(columns=["Dimension", "Indicative Code", "Evidence Extract"])
    return df


def stakeholder_df():
    return pd.DataFrame({"Stakeholder": list(STAKEHOLDERS.keys()), "Prevention Role": list(STAKEHOLDERS.values())})
