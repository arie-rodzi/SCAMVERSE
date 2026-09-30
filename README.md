# SCAMVERSE

**Online Investment Scam Ecosystem Intelligence Platform: v3.0**

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

1. **Upload and Analyse**: upload one or more `.txt` / `.docx` transcripts (paragraphs and tables are read) or paste text, then click *Analyse Corpus*. Under *Options* you can keep or remove speaker labels (`Officer A:`), choose which speakers' turns to exclude (default: `Interviewer`), and upload a custom lexicon (JSON). **Confidential transcripts should be analysed with a local installation**; text uploaded to a hosted instance is processed on that host.
2. **Dashboard** (`app.py`): warning-signal index and band, active dimensions, active indicators, word count, dimension-strength bar chart and risk-indicator radar.
3. **Thematic Evidence**: coding-evidence table (dimension, indicative code, verbatim extract), dimension sunburst and evidence extracts per dimension.
4. **Ecosystem Map**: directed reference graph of scam actors and institutions, with the stakeholder prevention matrix.
5. **Framework Model**: IMSPF formulation and six prevention layers.
6. **Report**: download the HTML report (standalone file) and the paginated A4 PDF report.
7. **About**: method summary, the full default lexicon, and a JSON export of it.

## Method

All analysis is in `modules/engine.py`, which has no Streamlit dependency.

- **Pre-processing.** Speaker turns start with `Label:` at the beginning of a line; interviewer turns are removed and labels stripped (configurable). White space is collapsed and a lower-cased copy is used for matching.
- **Matching.** Each lexicon term is matched as a whole term (not inside a longer word), with an optional ending `-s`, `-es`, `-d`, `-ed` or `-ing`. For example, `sc` matches "SC" but not "scam", and `guarantee` matches "guaranteed". Overlapping matches within one dimension or indicator (e.g. `high return` and `return`) are counted once.
- **Thematic coding.** `THEME_KEYWORDS` maps eight ecosystem dimensions to keyword lists. A dimension's evidence frequency is the total number of keyword matches; up to five sentences per dimension are kept as evidence, each coded with the first keyword it contains.
- **Risk index.** `RISK_RULES` maps eight warning indicators to keyword lists. Each indicator's hits are capped at `RISK_CAP = 5`, summed, and scaled to `score = floor(100 · Σ min(hits, 5) / (5 · 8))`. Bands: High ≥ 70, Moderate ≥ 35, otherwise Low. Because the cap makes the index saturate on long corpora, each indicator's uncapped density (matches per 1,000 words) is reported alongside it.
- **Terms.** Tokens of four or more letters, minus a stop-word list, ranked by frequency.

The analysis is deterministic: the same text and lexicon always give the same output. Reports print the software version and SHA-256 fingerprints of the lexicon and the corpus. To change the lexicon, upload a JSON file with the structure `{"dimensions": {name: [terms]}, "indicators": {name: [terms]}}` (export the default from the About page), or edit `THEME_KEYWORDS` / `RISK_RULES` in `modules/engine.py`.

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
examples/              synthetic demo transcript and runtime benchmark
.streamlit/config.toml light interface theme
```

## Tests and benchmark

```bash
pip install -r requirements-dev.txt
pytest                         # 31 test cases; also run by GitHub Actions on Python 3.9, 3.11, 3.12
pytest --cov=modules           # statement coverage
python examples/benchmark.py   # engine runtime at 1k to 250k words
```

## Example data

`examples/demo_transcript.txt` is a short **synthetic** transcript written for demonstration. It describes no real persons or cases. Upload it on the *Upload and Analyse* page with the default options to reproduce the walkthrough in the paper (see `examples/README.md`).

## Deployment

The repository deploys directly to Streamlit Community Cloud with `app.py` as the entry point; the platform installs `requirements.txt`.

## Limitations

The engine is lexicon-based and English-only and does not interpret context, so negations are counted and synonyms outside the lexicon are missed. General terms such as `account`, `bank` and `company` lower precision, and the default lexicon has not yet been validated against expert coding. Some terms belong to more than one dimension. The risk index is capped, so large corpora usually reach the upper band; use the per-1,000-word densities to compare corpora. The ecosystem map is a fixed reference structure, not derived from the uploaded text. Output is a first pass for human analysts, not a judgement about any individual case.

## Support

Zahari Md Rodzi: zahari@uitm.edu.my
