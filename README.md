# SCAMVERSE

**Online Investment Scam Ecosystem Intelligence Platform — v3.0**

SCAMVERSE is an open-source, multi-page Streamlit application that turns interview and case transcripts about online investment scams into structured ecosystem intelligence: lexicon-based thematic coding across eight ecosystem dimensions, a bounded warning-signal risk index over eight indicators, interactive Plotly charts, a NetworkX ecosystem map, a stakeholder prevention matrix, and downloadable HTML and PDF reports. It is the software companion to the Integrated Multi-Stakeholder Prevention Framework (IMSPF).

- **Live app:** https://scamverse.streamlit.app
- **License:** BSD 3-Clause (see `LICENSE`)
- **Citation:** see `CITATION.cff`

## Installation

Requires Python 3.9 or later.

```bash
git clone https://github.com/arie-rodzi/SCAMVERSE.git
cd SCAMVERSE
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. No database or external service is needed; all analysis state is held in the Streamlit session.

## Usage

1. **Upload & Analyse** — upload one or more `.txt` / `.docx` transcripts (paragraphs and tables are read) or paste text, then click *Analyse Corpus*.
2. **Dashboard** (`app.py`) — risk score and band, active dimensions, active indicators, word count, dimension-strength bar chart and risk-indicator radar.
3. **Thematic Evidence** — coding-evidence table (dimension, indicative code, verbatim extract), dimension sunburst and evidence extracts per dimension.
4. **Ecosystem Map** — directed reference graph of scam actors and institutions, with the stakeholder action matrix.
5. **Framework Model** — IMSPF formulation and six prevention layers.
6. **Report** — download the HTML report (standalone file) and the paginated A4 PDF report.
7. **About** — system description.

## Method

All analysis is in `modules/engine.py`, which has no Streamlit dependency.

- **Matching.** Text is lower-cased and each lexicon term is counted as a whole term (not inside a longer word), with an optional plural `s`/`es`. For example, `sc` matches “SC” but not “scam”.
- **Thematic coding.** `THEME_KEYWORDS` maps eight ecosystem dimensions to keyword lists. A dimension's evidence frequency is the total number of keyword matches; up to five sentences per dimension are kept as evidence, each coded with the first keyword it contains.
- **Risk index.** `RISK_RULES` maps eight warning indicators to keyword lists. Each indicator's hits are capped at 5, summed, and scaled to `score = floor(100 · Σ min(hits, 5) / (5 · 8))`. Bands: High ≥ 70, Moderate ≥ 35, otherwise Low.
- **Terms.** Tokens of four or more letters, minus a stop-word list, ranked by frequency.

The analysis is deterministic: the same input always gives the same output. To add a dimension or indicator, extend `THEME_KEYWORDS` or `RISK_RULES`.

## Project structure

```
app.py                 Dashboard (entry point)
config.py              App name, version and theme constants
modules/parser.py      .txt / .docx text extraction
modules/engine.py      Thematic coding, risk scoring, term extraction
modules/graphs.py      Plotly charts and NetworkX ecosystem graph
modules/reporting.py   HTML and PDF report builders
modules/ui.py          Shared layout helpers and CSS loader
pages/                 Six Streamlit pages (Upload, Thematic Evidence, Ecosystem Map,
                       Framework Model, Report, About)
assets/styles.css      Styling
tests/                 pytest suite
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deployment

The repository deploys directly to Streamlit Community Cloud with `app.py` as the entry point; the platform installs `requirements.txt`.

## Limitations

The engine is lexicon-based and English-only. Counts depend on the wording of the keyword lists, and the risk index is capped, so large corpora will usually reach the upper band. The ecosystem map is a fixed reference structure, not derived from the uploaded text.

## Support

Eley Suzana Kasim — eley@uitm.edu.my
