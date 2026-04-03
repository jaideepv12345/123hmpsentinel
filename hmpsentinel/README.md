# HMPSentinel v2.0

**Hazard Mitigation Plan Stress-Test Engine**

Built with Python (Flask) and deployed on Vercel as a serverless function.
Evaluates FEMA 44 CFR 201.6 compliance, BRIC competitiveness, Equity/Justice40, Climate Foresight, and Risk Quantification.

---

## Project Structure

```
hmpsentinel/
├── api/
│   ├── app.py                    ← Flask app (Vercel entry point)
│   ├── __init__.py
│   ├── analyzer/
│   │   ├── cfr_compliance.py     ← FEMA 44 CFR 201.6 analysis
│   │   ├── bric_analysis.py      ← BRIC competitiveness scoring
│   │   ├── equity_justice.py     ← Justice40 / CEJST analysis
│   │   ├── climate_analysis.py   ← Climate foresight analysis
│   │   └── risk_quantifier.py    ← Risk quantification
│   └── utils/
│       ├── pdf_processor.py      ← PDF text extraction
│       └── text_cleaner.py       ← Text normalization
├── public/
│   ├── styles.css                ← Frontend styles
│   └── script.js                 ← Frontend logic
├── templates/
│   └── index.html                ← Main dashboard
├── requirements.txt
├── vercel.json                   ← Vercel deployment config
└── README.md
```

---

## Deploy to Vercel via GitHub

### Step 1 — Initialize Git repository

```bash
cd hmpsentinel
git init
git add .
git commit -m "Initial commit: HMPSentinel v2.0"
```

### Step 2 — Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/hmpsentinel.git
git branch -M main
git push -u origin main
```

### Step 3 — Import into Vercel

1. Go to [vercel.com](https://vercel.com) and log in (or sign up free).
2. Click **"Add New Project"**.
3. Click **"Import Git Repository"** and select `hmpsentinel`.
4. On the Configure Project screen:
   - **Framework Preset:** `Other`
   - **Root Directory:** *(leave blank — use repo root)*
   - **Build Command:** *(leave blank)*
   - **Output Directory:** *(leave blank)*
5. Click **Deploy**.

Vercel will detect `vercel.json` automatically and deploy the Flask app as a Python serverless function.

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
cd api
flask run --port 5000
```

Then open [http://localhost:5000](http://localhost:5000).

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main dashboard UI |
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Upload PDF and run full stress-test |

### POST `/api/analyze` — Form fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File (PDF) | Yes | Hazard Mitigation Plan PDF |
| `county` | string | Yes | County name (e.g., `Guilford County`) |
| `state` | string | Yes | State abbreviation (e.g., `NC`) |
| `plan_year` | number | No | Plan adoption year |
| `plan_type` | string | No | `Single Jurisdiction` or `Multi-jurisdictional` |
| `plan_title` | string | No | Plan title |

---

## Decision Framework Applied

The code base was selected using the **@Decision** prompt from the internal prompts library v5:

| Criterion | Weight | GLM5 | Minimax | O3 |
|-----------|--------|------|---------|-----|
| Vercel/Python deployment readiness | 30% | 70 | **95** | 60 |
| Analysis depth & CFR coverage | 25% | 75 | **90** | 85 |
| Output schema completeness | 20% | 65 | 80 | **95** |
| Code quality & syntax validity | 15% | 60 | **85** | 80 |
| Frontend UX completeness | 10% | 55 | **90** | 50 |
| **Weighted Total** | | 67.25 | **88.25** | 74.75 |

**Winner: Minimax** as the base architecture.
**GLM5** OCR/jurisdiction validation logic merged into `app.py`.
**O3** output schema (thesis, stress_tests, funding_triage, temporal_phases, next_3_actions, top_risks, falsification) merged into the API response.

---

*HMPSentinel v2.0 — Operational Hazard Mitigation Plan Analysis. This tool provides directional assessment, not formal FEMA determination.*
