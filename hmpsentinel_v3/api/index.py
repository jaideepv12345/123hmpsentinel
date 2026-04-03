"""
HMPSentinel v2.0 - Hazard Mitigation Plan Stress-Test Engine
Decision: Minimax (base) + GLM5 OCR validation + O3 output schema
Vercel-compatible serverless function (Python / Flask)
"""

import os
import re
import sys
import json
import traceback
from datetime import datetime, date

# ── Path setup ──────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))  # .../api/
_ROOT = os.path.dirname(_HERE)                       # repo root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Import analyzers
from lib.analyzer.cfr_compliance import CFRComplianceAnalyzer
from lib.analyzer.bric_analysis import BRICAnalyzer
from lib.analyzer.equity_justice import EquityJusticeAnalyzer
from lib.analyzer.climate_analysis import ClimateAnalyzer
from lib.analyzer.risk_quantifier import RiskQuantifier

# Import utilities
from lib.utils.pdf_processor import PDFProcessor
from lib.utils.text_cleaner import TextCleaner

# ── Flask app setup ───────────────────────────────────────────────────────────



_STATIC = os.path.join(_ROOT, 'static')
app = Flask(__name__, static_folder=_STATIC, static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.config['UPLOAD_FOLDER'] = '/tmp'

# ── Initialise analyzers once at cold-start ───────────────────────────────────
cfr_analyzer    = CFRComplianceAnalyzer()
bric_analyzer   = BRICAnalyzer()
equity_analyzer = EquityJusticeAnalyzer()
climate_analyzer = ClimateAnalyzer()
risk_quantifier  = RiskQuantifier()
pdf_processor    = PDFProcessor()
text_cleaner     = TextCleaner()

# ── GLM5 Ground-Truth Jurisdiction Database (merged from GLM5) ────────────────
KNOWN_JURISDICTIONS = {
    "guilford": [
        "Guilford County", "Greensboro", "High Point", "Gibsonville",
        "Jamestown", "Oak Ridge", "Pleasant Garden", "Sedalia",
        "Stokesdale", "Summerfield", "Whitsett", "Burlington"
    ],
    "default": []   # Extend this dict for other counties as needed
}

JURISDICTION_PATTERN = re.compile(
    r'(Town|City|Village|County|Borough)\s+of\s+([A-Za-z][A-Za-z\s]{1,30})',
    re.IGNORECASE
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main dashboard."""
    html_path = os.path.join(_ROOT, 'static', 'index.html')
    return send_from_directory(os.path.dirname(html_path), os.path.basename(html_path))


@app.route('/styles.css')
def styles():
    return send_from_directory(_STATIC, 'styles.css')


@app.route('/script.js')
def script():
    return send_from_directory(_STATIC, 'script.js')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'HMPSentinel',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_plan():
    """
    Main analysis endpoint.
    Accepts a PDF upload and returns a structured stress-test report
    following the O3 depth-10 operational output schema.
    """
    start_time = datetime.utcnow()

    try:
        # ── Validate request ──────────────────────────────────────────────────
        if 'file' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400

        # ── Form metadata ─────────────────────────────────────────────────────
        county_name = request.form.get('county', 'Unknown County')
        state       = request.form.get('state', 'Unknown State')
        plan_year   = request.form.get('plan_year', 'Unknown')
        plan_type   = request.form.get('plan_type', 'Single Jurisdiction')
        plan_title  = request.form.get('plan_title', 'Hazard Mitigation Plan')

        # ── Save & extract PDF ────────────────────────────────────────────────
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        raw_text = pdf_processor.extract_text(filepath)
        if not raw_text or len(raw_text.strip()) < 500:
            return jsonify({
                'error': (
                    'Unable to extract sufficient text from PDF. '
                    'The document may be scanned or password-protected.'
                )
            }), 400

        cleaned_text = text_cleaner.clean(raw_text)

        # ── GLM5 OCR / Jurisdiction Validation ───────────────────────────────
        jurisdiction_validation = _validate_jurisdictions(
            cleaned_text, county_name.lower().split()[0]
        )

        # ── Plan metadata (GLM5 expiry logic) ────────────────────────────────
        plan_metadata = _extract_plan_metadata(cleaned_text, plan_year)

        # ── Detect jurisdictions ──────────────────────────────────────────────
        jurisdictions = _detect_jurisdictions(cleaned_text)

        # ── Run all analysis modules (Minimax) ────────────────────────────────
        cfr_results     = cfr_analyzer.analyze(cleaned_text, jurisdictions)
        bric_results    = bric_analyzer.analyze(cleaned_text)
        equity_results  = equity_analyzer.analyze(cleaned_text)
        climate_results = climate_analyzer.analyze(cleaned_text)
        risk_results    = risk_quantifier.analyze(cleaned_text, county_name, state)

        # ── Compile O3-schema output ──────────────────────────────────────────
        end_time        = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        results = {
            # ── O3 Thesis block ───────────────────────────────────────────────
            'thesis': _build_thesis(
                county_name, plan_year,
                cfr_results, bric_results, equity_results, risk_results
            ),

            # ── Metadata ──────────────────────────────────────────────────────
            'metadata': {
                'service': 'HMPSentinel',
                'version': '2.0.0',
                'processing_timestamp': end_time.isoformat(),
                'processing_time_seconds': round(processing_time, 2),
                'input_file': filename,
                'county': county_name,
                'state': state,
                'plan_year': plan_year,
                'plan_type': plan_type
            },

            # ── County identity ───────────────────────────────────────────────
            'county_identity': {
                'county': county_name,
                'state': state,
                'plan_title': plan_title,
                'plan_year': plan_year,
                'plan_type': plan_type,
                'plan_status': plan_metadata['status'],
                'plan_age_years': plan_metadata['age'],
                'is_expired': plan_metadata['is_expired'],
                'jurisdictions_detected': jurisdictions,
                'data_freshness': _determine_freshness(cleaned_text, plan_year)
            },

            # ── GLM5 OCR validation ───────────────────────────────────────────
            'jurisdiction_validation': jurisdiction_validation,

            # ── Core analysis modules (Minimax) ───────────────────────────────
            'cfr_compliance':    cfr_results,
            'bric_readiness':    bric_results,
            'equity_justice':    equity_results,
            'climate_foresight': climate_results,
            'risk_quantification': risk_results,

            # ── O3-style structured outputs ───────────────────────────────────
            'stress_tests':         _build_stress_tests(cfr_results, bric_results, equity_results, risk_results),
            'funding_triage':       _build_funding_triage(cfr_results, bric_results, risk_results),
            'temporal_phases':      _build_temporal_phases(cfr_results, climate_results),
            'priority_findings':    _compile_findings(cfr_results, bric_results, equity_results, climate_results, risk_results),
            'fema_readiness':       _assess_fema_readiness(cfr_results),
            'recommendations':      _generate_recommendations(cfr_results, bric_results, equity_results, climate_results),
            'decision_implications': _build_decision_implications(cfr_results, bric_results, equity_results),
            'next_3_actions':       _build_next_actions(cfr_results, bric_results, equity_results),
            'top_risks':            _build_top_risks(cfr_results, risk_results),
            'what_would_change_my_mind': _build_falsification(cfr_results, bric_results),
            'signature_artifact': (
                f"HMPSentinel_OPS-INSIGHT_{county_name.upper().replace(' ', '_')}_"
                f"{end_time.strftime('%Y-%m-%dT%H:%MZ')}"
            )
        }

        # ── Cleanup ───────────────────────────────────────────────────────────
        try:
            os.remove(filepath)
        except Exception:
            pass

        return jsonify(results)

    except Exception as exc:
        traceback.print_exc()
        return jsonify({
            'error': f'Analysis failed: {str(exc)}',
            'details': traceback.format_exc()
        }), 500


# ── Helper functions ──────────────────────────────────────────────────────────

def _extract_plan_metadata(text: str, plan_year_input: str) -> dict:
    """GLM5-derived: extract plan year and compute FEMA 5-year expiry."""
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if plan_year_input not in ('Unknown', ''):
        try:
            plan_year = int(plan_year_input)
        except ValueError:
            plan_year = int(max(set(years), key=years.count)) if years else date.today().year
    else:
        plan_year = int(max(set(years), key=years.count)) if years else date.today().year

    current_year = date.today().year
    age = current_year - plan_year
    is_expired = age >= 5

    return {
        'plan_year': plan_year,
        'current_year': current_year,
        'age': age,
        'status': 'EXPIRED / UPDATE REQUIRED' if is_expired else 'ACTIVE',
        'is_expired': is_expired
    }


def _validate_jurisdictions(text: str, county_key: str) -> dict:
    """
    GLM5-derived OCR/jurisdiction validation.
    Compares extracted names against the KNOWN_JURISDICTIONS ground-truth DB.
    Flags partial matches as potential OCR artefacts.
    """
    known_list = KNOWN_JURISDICTIONS.get(county_key, KNOWN_JURISDICTIONS.get('default', []))
    known_set  = {n.lower() for n in known_list}

    raw_matches = JURISDICTION_PATTERN.findall(text)
    extracted   = [f"{t} of {n.strip()}" for t, n in raw_matches]

    valid_jurisdictions  = []
    flagged_ocr_errors   = []

    for name in extracted:
        clean = re.sub(r'(town|city|village|county|borough)\s+of\s+', '', name.lower()).strip()

        found = False
        for known in known_set:
            if clean in known or known in clean:
                valid_jurisdictions.append(name.title())
                found = True
                break

        if not found and len(clean) > 3:
            partial = [k for k in known_set if clean in k]
            if partial:
                flagged_ocr_errors.append({
                    'found': name,
                    'suggestion': partial[0].title(),
                    'reason': 'Partial match / possible OCR artefact',
                    'tag': 'Observed'
                })
            elif known_list:   # Only flag if we have a known DB for this county
                flagged_ocr_errors.append({
                    'found': name,
                    'suggestion': 'Unknown',
                    'reason': 'Jurisdiction not in county ground-truth database',
                    'tag': 'Inferred'
                })

    trust_score = max(0, 100 - len(flagged_ocr_errors) * 10)

    return {
        'validated_jurisdictions': list(set(valid_jurisdictions)),
        'ocr_errors_detected': flagged_ocr_errors,
        'trust_score': trust_score,
        'note': (
            'Ground-truth DB active for this county.' if known_list
            else 'No ground-truth DB for this county — OCR validation skipped.'
        )
    }


def _detect_jurisdictions(text: str) -> list:
    """Detect municipality names from plan text."""
    terms = ['Town of', 'City of', 'Village of', 'Borough of', 'County of']
    found = set()
    for line in text.split('\n'):
        for term in terms:
            if term.lower() in line.lower():
                parts = line.split(term)
                if len(parts) > 1:
                    name = parts[1].strip().split(',')[0].strip()
                    if 2 < len(name) < 50:
                        found.add(name)
    return sorted(found)[:20]


def _determine_freshness(text: str, plan_year: str) -> str:
    try:
        yr = int(plan_year)
    except (ValueError, TypeError):
        yr = 0
    recent = any(str(y) in text for y in range(2020, 2027))
    if yr >= 2020 or (yr == 0 and recent):
        return 'Current'
    elif yr >= 2016:
        return 'Moderate'
    return 'Outdated (pre-2016 risk baseline)'


def _build_thesis(county, plan_year, cfr, bric, equity, risk) -> str:
    """O3-style one-sentence thesis summarising the plan's overall posture."""
    cfr_score  = cfr.get('overall_score', 0)
    bric_score = bric.get('overall_score', 0)
    eq_score   = equity.get('equity_score', 0)

    if cfr_score >= 85 and bric_score >= 75:
        posture = "is on track for FEMA approval"
    elif cfr_score >= 70:
        posture = "meets minimum FEMA thresholds but requires targeted improvements"
    else:
        posture = "has significant compliance gaps that must be resolved before FEMA submission"

    return (
        f"{county}'s {plan_year} Hazard Mitigation Plan {posture}. "
        f"CFR compliance score: {cfr_score}%, BRIC readiness: {bric_score}%, "
        f"Equity/Justice40 score: {eq_score}%. "
        "Key risks include under-quantified loss exposure, incomplete equity overlays, "
        "and potential BCA friction on high-value projects."
    )


def _build_stress_tests(cfr, bric, equity, risk) -> list:
    """O3-style ordered stress-test list derived from analysis gaps."""
    tests = []
    order = 0

    for element, data in cfr.get('element_assessment', {}).items():
        if data.get('status') in ['Missing', 'Weak']:
            tests.append({
                'order': order,
                'claim': f"CFR element '{data.get('name', element)}' is {data.get('status', 'weak')}.",
                'evidence': data.get('finding', 'Indicator count below threshold.'),
                'mechanism': 'Missing element severs FEMA reviewer traceability and may trigger conditional approval.',
                'tag': 'Observed',
                'decision_implication': data.get('remediation_hint', 'Document and quantify this element.')
            })
            order += 1

    for gap in bric.get('gaps', []):
        tests.append({
            'order': order,
            'claim': f"BRIC criterion '{gap.get('criterion', '')}' is under-addressed.",
            'evidence': gap.get('description', ''),
            'mechanism': 'Weak BRIC criterion reduces competitive score in BRIC/HMGP applications.',
            'tag': 'Inferred',
            'decision_implication': gap.get('recommendation', 'Strengthen this criterion.')
        })
        order += 1

    for gap in equity.get('gaps', []):
        tests.append({
            'order': order,
            'claim': f"Equity gap: '{gap.get('name', '')}'.",
            'evidence': gap.get('description', ''),
            'mechanism': 'Missing Justice40/CEJST alignment forfeits competitive scoring points.',
            'tag': 'Observed',
            'decision_implication': gap.get('recommendation', 'Integrate CEJST tract data.')
        })
        order += 1

    return tests


def _build_funding_triage(cfr, bric, risk) -> list:
    """O3-style funding triage: SUBMISSION_READY / CONDITIONAL / FUNDING_BLOCKED."""
    bric_score = bric.get('overall_score', 0)
    cfr_score  = cfr.get('overall_score', 0)
    risk_score = risk.get('risk_quantification_score', 0)

    triage = []

    if bric_score >= 75 and cfr_score >= 80:
        triage.append({
            'action': 'Highest-scoring BRIC-eligible projects',
            'status': 'SUBMISSION_READY',
            'match_gap': 'Low — confirm local match commitment',
            'bca_readiness': 'High — verify cost index is current'
        })
    elif bric_score >= 55:
        triage.append({
            'action': 'Moderate BRIC projects',
            'status': 'CONDITIONAL',
            'match_gap': 'Medium — local match may be unsecured',
            'bca_readiness': 'Moderate — downtime metrics or equity overlay may be missing'
        })
    else:
        triage.append({
            'action': 'Low-scoring projects',
            'status': 'FUNDING_BLOCKED',
            'match_gap': 'High — no dedicated reserve identified',
            'bca_readiness': 'Low — tract-level data and relocation plan absent'
        })

    if risk_score < 50:
        triage.append({
            'action': 'Floodplain acquisition / property protection',
            'status': 'FUNDING_BLOCKED',
            'match_gap': 'High — acquisition cost and match unsecured',
            'bca_readiness': 'Low — tract-level exposure data missing'
        })

    return triage


def _build_temporal_phases(cfr, climate) -> dict:
    """O3-style acute / recovery / adaptation temporal breakdown."""
    return {
        'acute': [
            'Real-time hazard sensor feeds and public warning systems',
            'Pre-staged portable generators or emergency contracts',
            'Multilingual public alert push notifications'
        ],
        'recovery': [
            'Permanent generator installation (Phase B)',
            'School and shelter facility retrofits',
            'Rapid debris removal contract activation'
        ],
        'adaptation': [
            'Green-infrastructure / nature-based solutions',
            'Floodplain buy-outs and greenway conversion',
            'Culvert and stormwater infrastructure upsizing to 25-year storm standard'
        ]
    }


def _compile_findings(cfr, bric, equity, climate, risk) -> list:
    """Prioritised findings list (HIGH / MEDIUM severity)."""
    findings = []

    for element, data in cfr.get('element_assessment', {}).items():
        if data.get('status') in ['Weak', 'Missing']:
            findings.append({
                'severity': 'HIGH' if data.get('status') == 'Missing' else 'MEDIUM',
                'category': 'FEMA Compliance',
                'finding': f"CFR Element {element} ({data.get('name', '')}): {data.get('status')}",
                'fema_action': data.get('reviewer_likely_action', 'May request additional documentation'),
                'remediation': data.get('remediation_hint', 'Document methodology and data sources'),
                'tag': 'Observed'
            })

    for gap in bric.get('gaps', []):
        findings.append({
            'severity': 'MEDIUM',
            'category': 'BRIC Competitiveness',
            'finding': gap.get('description', 'Gap detected'),
            'fema_action': 'May reduce competitiveness in BRIC applications',
            'remediation': gap.get('recommendation', 'Add required elements to projects'),
            'tag': 'Inferred'
        })

    for gap in equity.get('gaps', []):
        findings.append({
            'severity': 'HIGH',
            'category': 'Equity / Justice40',
            'finding': gap.get('description', 'Gap detected'),
            'fema_action': 'Justice40 compliance may be questioned',
            'remediation': gap.get('recommendation', 'Integrate CEJST data'),
            'tag': 'Observed'
        })

    for gap in risk.get('gaps', []):
        findings.append({
            'severity': 'MEDIUM',
            'category': 'Risk Quantification',
            'finding': gap.get('gap', 'Gap detected'),
            'fema_action': 'May request quantified exposure data',
            'remediation': gap.get('recommendation', 'Conduct exposure analysis'),
            'tag': 'Inferred'
        })

    severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    findings.sort(key=lambda x: severity_order.get(x['severity'], 2))
    return findings[:15]


def _assess_fema_readiness(cfr) -> dict:
    high = sum(1 for d in cfr.get('element_assessment', {}).values() if d.get('status') == 'Missing')
    med  = sum(1 for d in cfr.get('element_assessment', {}).values() if d.get('status') == 'Weak')

    if high > 2:
        return {
            'status': 'Not Ready',
            'description': f'{high} fundamental CFR gaps require substantial rework.',
            'action_required': 'Address all high-severity CFR gaps before submission.'
        }
    elif high > 0 or med > 3:
        return {
            'status': 'Conditional Approval Likely',
            'description': f'{high} critical and {med} moderate gaps. Conditional approval expected.',
            'action_required': 'Address high-severity gaps and prepare documentation for moderate items.'
        }
    return {
        'status': 'Ready to Submit',
        'description': 'Plan appears to meet most FEMA 44 CFR 201.6 requirements.',
        'action_required': 'Proceed with formal FEMA submission.'
    }


def _generate_recommendations(cfr, bric, equity, climate) -> dict:
    recs = {'immediate': [], 'near_term': [], 'medium_term': [], 'long_term': []}

    for element, data in cfr.get('element_assessment', {}).items():
        if data.get('status') == 'Missing':
            recs['immediate'].append({
                'priority': 'HIGH',
                'action': f"Add missing CFR element: {element} — {data.get('name', '')}",
                'details': data.get('remediation_hint', 'Document required element'),
                'timeline': '0-30 days'
            })

    if bric.get('overall_score', 0) < 80:
        recs['near_term'].append({
            'priority': 'MEDIUM',
            'action': 'Enhance BRIC competitiveness',
            'details': 'Add innovation, climate, equity narratives to mitigation projects',
            'timeline': '30-90 days'
        })

    if equity.get('equity_score', 0) < 70:
        recs['medium_term'].append({
            'priority': 'HIGH',
            'action': 'Integrate Justice40 / CEJST framework',
            'details': 'Add CEJST tract IDs, disadvantaged community identification, and engagement plan',
            'timeline': '3-6 months'
        })

    if climate.get('climate_score', 0) < 70:
        recs['medium_term'].append({
            'priority': 'MEDIUM',
            'action': 'Strengthen climate risk integration',
            'details': 'Add future scenario analysis and compound hazard narratives',
            'timeline': '3-6 months'
        })

    recs['long_term'].append({
        'priority': 'LOW',
        'action': 'Comprehensive plan update cycle',
        'details': 'Rebuild risk assessment with current data, climate scenarios, and equity frameworks',
        'timeline': 'Next plan update cycle (5-year)'
    })

    return recs


def _build_decision_implications(cfr, bric, equity) -> list:
    implications = []
    cfr_score  = cfr.get('overall_score', 0)
    bric_score = bric.get('overall_score', 0)
    eq_score   = equity.get('equity_score', 0)

    if cfr_score < 70:
        implications.append(
            'Secure board resolution to fund plan update — current compliance score is below FEMA threshold.'
        )
    if bric_score < 75:
        implications.append(
            'Bundle equity overlays (CEJST tracts, relocation stipends) into BRIC narratives to unlock Justice40 score multipliers.'
        )
    if eq_score < 60:
        implications.append(
            'Integrate CEJST screening tool data and document community engagement before next BRIC NOFO.'
        )
    implications.append(
        'Sequence projects to match realistic staff throughput — prefer 2 concurrent capital projects, not 5.'
    )
    return implications


def _build_next_actions(cfr, bric, equity) -> list:
    actions = []
    missing = [
        f"{d.get('name', e)}"
        for e, d in cfr.get('element_assessment', {}).items()
        if d.get('status') == 'Missing'
    ]
    if missing:
        actions.append(
            f"Hold cross-walk workshop to document missing CFR elements: {', '.join(missing[:3])}."
        )
    if bric.get('overall_score', 0) < 75:
        actions.append(
            'Commission 30-day mini-BCA on highest-value project with state EM support to validate BCR ≥ 1.0.'
        )
    if equity.get('equity_score', 0) < 70:
        actions.append(
            'Insert CEJST tract IDs and renter relocation stipend language into acquisition action sheets before BRIC NOFO drop.'
        )
    if not actions:
        actions.append('Review all conditional CFR elements and prepare supplemental documentation for FEMA submission.')
    return actions[:3]


def _build_top_risks(cfr, risk) -> list:
    risks = []
    for element, data in cfr.get('element_assessment', {}).items():
        if data.get('status') == 'Missing':
            risks.append(f"Missing CFR element '{data.get('name', element)}' — FEMA rejection risk.")
    for gap in risk.get('gaps', [])[:2]:
        risks.append(gap.get('gap', 'Risk quantification gap.'))
    risks.append('Local match financing gap may stall high-value projects at Notice of Award.')
    return risks[:5]


def _build_falsification(cfr, bric) -> str:
    return (
        "If the jurisdiction produces a signed ordinance reserving ≥ $2 M for FEMA local matches, "
        "certifies two BCA-trained staff, and inserts CEJST tract IDs into all acquisition action sheets, "
        "most 'conditional' ratings would flip to 'submission ready'."
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
