import re
from collections import Counter, defaultdict
import pandas as pd

THEME_KEYWORDS = {
    "Digital Recruitment Infrastructure": ["telegram", "facebook", "whatsapp", "wechat", "social media", "group", "link", "ads", "online", "platform"],
    "Psychological Manipulation & Legitimacy Cues": ["guarantee", "profit", "return", "dividend", "testimonial", "receipt", "urgent", "bonus", "promise", "trust"],
    "Victim Vulnerability & Decision Behaviour": ["victim", "retiree", "teacher", "student", "professional", "nurse", "lecturer", "greed", "young", "older", "salary"],
    "Scammer Operational Architecture": ["syndicate", "mastermind", "call center", "agent", "script", "fake", "company", "seminar", "package", "slot"],
    "Financial Transaction & Laundering Chain": ["bank", "account", "mule", "atm", "transfer", "tac", "crypto", "wallet", "money", "layer"],
    "Institutional Response & Enforcement": ["police", "pdrm", "bnm", "bank negara", "ssm", "skmm", "sc", "nsrc", "bukit aman", "ipk", "ipd", "section 420"],
    "Evidence, Investigation & Prosecution": ["evidence", "receipt", "report", "statement", "investigation", "court", "arrest", "dpp", "nfa", "charge"],
    "Prevention, Awareness & Public Resilience": ["awareness", "campaign", "education", "prevent", "hotline", "mule check", "alert", "seminar", "tips"],
}

RISK_RULES = {
    "Unrealistic high return": ["high return", "30%", "300%", "profit", "return", "dividend", "bonus", "rm50,000", "million"],
    "Guaranteed profit or no-risk claim": ["guarantee", "guaranteed", "confirm", "no risk", "risk-free", "sure profit"],
    "Telegram or social media recruitment": ["telegram", "facebook", "whatsapp", "wechat", "social media", "link"],
    "Mule account or layered transfer": ["mule", "account", "atm", "transfer", "bank", "layer", "money out"],
    "Fake testimonial or fabricated proof": ["testimonial", "receipt", "screenshot", "proof", "dividend received", "got my profit"],
    "Unlicensed or unclear investment entity": ["no license", "unlicensed", "ssm", "bank negara", "bnm", "not listed", "company"],
    "Crypto or cross-border laundering": ["crypto", "cryptocurrency", "bitcoin", "overseas", "out of the country", "foreign"],
    "Urgency pressure": ["urgent", "immediate", "short period", "limited", "act now", "within 3 hours"],
}

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

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def split_sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_text(text)) if len(s.strip()) > 20]

def analyze_text(text: str):
    lower = text.lower()
    sentences = split_sentences(text)
    theme_counts = {}
    evidence = defaultdict(list)
    codes = []
    for theme, keys in THEME_KEYWORDS.items():
        count = sum(lower.count(key) for key in keys)
        theme_counts[theme] = count
        for sent in sentences:
            s_lower = sent.lower()
            hit_keys = [k for k in keys if k in s_lower]
            if hit_keys:
                evidence[theme].append(sent[:420])
                codes.append({"Dimension": theme, "Indicative Code": hit_keys[0].title(), "Evidence Extract": sent[:360]})
                if len(evidence[theme]) >= 5:
                    break
    risk_hits = {rule: sum(lower.count(k) for k in keys) for rule, keys in RISK_RULES.items()}
    raw_score = sum(min(v, 5) for v in risk_hits.values())
    risk_score = min(100, int(raw_score / (len(RISK_RULES) * 5) * 100))
    risk_level = "High" if risk_score >= 70 else "Moderate" if risk_score >= 35 else "Low"
    words = re.findall(r"[A-Za-z]{4,}", lower)
    top_terms = Counter([w for w in words if w not in STOPWORDS]).most_common(30)
    return {"text": text, "theme_counts": theme_counts, "evidence": dict(evidence), "risk_hits": risk_hits, "risk_score": risk_score, "risk_level": risk_level, "top_terms": top_terms, "codes": codes}

def theme_df(analysis):
    counts = analysis["theme_counts"]
    total = sum(counts.values()) or 1
    return pd.DataFrame({"Dimension": list(counts.keys()), "Evidence Frequency": list(counts.values()), "Relative Weight": [round(v/total, 3) for v in counts.values()]}).sort_values("Evidence Frequency", ascending=False)

def risk_df(analysis):
    hits = analysis["risk_hits"]
    return pd.DataFrame({"Risk Indicator": list(hits.keys()), "Detected Evidence": list(hits.values()), "Interpretation": ["Strong signal" if v>=3 else "Present" if v>0 else "Not detected" for v in hits.values()]})

def codes_df(analysis):
    df = pd.DataFrame(analysis.get("codes", []))
    if df.empty:
        return pd.DataFrame(columns=["Dimension", "Indicative Code", "Evidence Extract"])
    return df

def stakeholder_df():
    return pd.DataFrame({"Stakeholder": list(STAKEHOLDERS.keys()), "Prevention Role": list(STAKEHOLDERS.values())})
