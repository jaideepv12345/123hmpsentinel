// static/script.js  –  HMPSentinel v2.1  (Vercel Blob upload flow)
// ─────────────────────────────────────────────────────────────────
// Upload flow:
//   1. User picks a PDF and fills the form
//   2. JS calls  GET /api/upload-token  → gets a short-lived Blob client token
//   3. JS uploads the PDF directly to Vercel Blob using that token
//      (bypasses the 4.5 MB Vercel edge payload limit)
//   4. JS sends  POST /api/analyze  with the Blob URL + form metadata
//   5. Python downloads the PDF from the Blob URL and runs analysis
// ─────────────────────────────────────────────────────────────────

let currentResults = null;

// ── Helper: upload file to Vercel Blob via client token ──────────────────────
async function uploadToBlob(file) {
    // Step 1: get a client upload token from our Python backend
    const tokenRes = await fetch('/api/upload-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.name, content_type: 'application/pdf' })
    });

    if (!tokenRes.ok) {
        const err = await tokenRes.json().catch(() => ({}));
        throw new Error(err.error || 'Failed to get upload token from server.');
    }

    const { upload_url, blob_url, token } = await tokenRes.json();

    // Step 2: PUT the file directly to Vercel Blob using the pre-signed URL
    const putRes = await fetch(upload_url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/pdf',
            'x-vercel-blob-token': token
        },
        body: file
    });

    if (!putRes.ok) {
        throw new Error(`Blob upload failed: HTTP ${putRes.status}`);
    }

    // Vercel Blob returns the final URL in the response body
    const blobData = await putRes.json().catch(() => null);
    return blobData?.url || blob_url;
}

// ── Main form submit ──────────────────────────────────────────────────────────
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];

    if (!file) {
        showError('Please select a PDF file.');
        return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Only PDF files are supported.');
        return;
    }

    const btn = document.getElementById('analyzeBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');

    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    hideError();

    try {
        // ── Step A: upload PDF to Vercel Blob ─────────────────────────────────
        updateStatus('Uploading PDF to secure storage…');
        const fileUrl = await uploadToBlob(file);

        // ── Step B: send URL + metadata to Python for analysis ────────────────
        updateStatus('Analyzing plan (this may take up to 60 seconds)…');
        const payload = {
            file_url:   fileUrl,
            filename:   file.name,
            county:     document.getElementById('county').value,
            state:      document.getElementById('state').value,
            plan_title: document.getElementById('plan_title').value,
            plan_year:  document.getElementById('plan_year').value,
            plan_type:  document.getElementById('plan_type').value
        };

        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // Always try to parse JSON — our backend guarantees it
        let data;
        try {
            data = await response.json();
        } catch (_) {
            throw new Error('Server returned an unexpected response. Check Vercel logs.');
        }

        if (!response.ok) {
            throw new Error(data.error || `Analysis failed (HTTP ${response.status})`);
        }

        currentResults = data;
        displayResults(data);

    } catch (error) {
        showError(error.message);
        document.getElementById('results').style.display = 'none';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        clearStatus();
    }
});

// ── UI helpers ────────────────────────────────────────────────────────────────
function showError(msg) {
    const el = document.getElementById('error');
    const msgEl = document.getElementById('errorMessage');
    if (el) el.style.display = 'block';
    if (msgEl) msgEl.textContent = msg;
}

function hideError() {
    const el = document.getElementById('error');
    if (el) el.style.display = 'none';
}

function updateStatus(msg) {
    let statusEl = document.getElementById('statusMessage');
    if (!statusEl) {
        statusEl = document.createElement('p');
        statusEl.id = 'statusMessage';
        statusEl.style.cssText = 'text-align:center;color:#4f46e5;font-size:0.95rem;margin-top:10px;';
        document.getElementById('analyzeBtn').insertAdjacentElement('afterend', statusEl);
    }
    statusEl.textContent = msg;
}

function clearStatus() {
    const el = document.getElementById('statusMessage');
    if (el) el.textContent = '';
}

// ── Results rendering ─────────────────────────────────────────────────────────
function displayResults(data) {
    hideError();
    document.getElementById('results').style.display = 'block';

    // County Identity
    const identity = data.county_identity;
    document.getElementById('countyIdentity').innerHTML = `
        <div class="element-grid">
            <div class="element-item"><strong>County:</strong> ${identity.county}</div>
            <div class="element-item"><strong>State:</strong> ${identity.state}</div>
            <div class="element-item"><strong>Plan Year:</strong> ${identity.plan_year}</div>
            <div class="element-item"><strong>Plan Type:</strong> ${identity.plan_type}</div>
            <div class="element-item"><strong>Jurisdictions:</strong> ${identity.jurisdictions_detected?.slice(0, 5).join(', ') || 'Not detected'}</div>
            ${data.metadata?.note ? `<div class="element-item" style="grid-column:1/-1;font-size:0.85rem;color:#6b7280;"><em>${data.metadata.note}</em></div>` : ''}
        </div>
    `;

    const freshnessBadge = document.getElementById('dataFreshness');
    freshnessBadge.textContent = identity.data_freshness;
    freshnessBadge.className = identity.data_freshness.includes('Outdated') ? 'badge danger' : 'badge success';

    // FEMA Readiness
    const readiness = data.fema_readiness;
    const statusEl = document.getElementById('femaReadinessStatus');
    statusEl.textContent = readiness.status;
    statusEl.className = 'readiness-status ' + (
        readiness.status.includes('Ready') ? 'ready' :
        readiness.status.includes('Conditional') ? 'conditional' : 'not-ready'
    );
    document.getElementById('femaReadinessContent').innerHTML = `
        <p>${readiness.description}</p>
        <p><strong>Action Required:</strong> ${readiness.action_required}</p>
    `;

    // CFR Compliance
    const cfr = data.cfr_compliance;
    document.getElementById('cfrScore').textContent = `${cfr.overall_score}%`;
    document.getElementById('cfrCompliance').innerHTML = generateCFRGrid(cfr.element_assessment);

    // BRIC Readiness
    const bric = data.bric_readiness;
    document.getElementById('bricScore').textContent = `${bric.overall_score}%`;
    document.getElementById('bricAnalysis').innerHTML = generateBRICSection(bric);

    // Equity
    const equity = data.equity_justice;
    document.getElementById('equityScore').textContent = `${equity.equity_score}%`;
    document.getElementById('equityAnalysis').innerHTML = generateEquitySection(equity);

    // Climate
    const climate = data.climate_foresight;
    document.getElementById('climateScore').textContent = `${climate.climate_score}%`;
    document.getElementById('climateAnalysis').innerHTML = generateClimateSection(climate);

    // Risk
    const risk = data.risk_quantification;
    document.getElementById('riskScore').textContent = `${risk.risk_quantification_score}%`;
    document.getElementById('riskAnalysis').innerHTML = generateRiskSection(risk);

    // Priority Findings
    document.getElementById('findingsCount').textContent = `${data.priority_findings.length} Findings`;
    document.getElementById('priorityFindings').innerHTML = generateFindingsList(data.priority_findings);

    // Recommendations
    document.getElementById('recommendations').innerHTML = generateRecommendations(data.recommendations);
}

function generateCFRGrid(elements) {
    let html = '<div class="element-grid">';
    for (const [id, data] of Object.entries(elements)) {
        html += `
            <div class="element-item ${data.status.toLowerCase().replace(' ', '-')}">
                <h4>${id}: ${data.name}</h4>
                <span class="status" style="color: ${getStatusColor(data.status)}">${data.status}</span>
                <p class="finding">${data.finding}</p>
            </div>
        `;
    }
    html += '</div>';
    return html;
}

function getStatusColor(status) {
    if (status === 'Present') return '#059669';
    if (status === 'Weak') return '#d97706';
    return '#dc2626';
}

function generateBRICSection(bric) {
    let html = `
        <div class="element-grid">
            <div class="element-item present">
                <h4>Overall Grade</h4>
                <span class="status">${bric.overall_grade}</span>
            </div>
        </div>
        <h4 style="margin-top: 15px">Criterion Scores:</h4>
        <div class="element-grid">
    `;
    for (const [criterion, data] of Object.entries(bric.criteria_scores)) {
        html += `
            <div class="element-item ${data.status === 'Well Addressed' ? 'present' : 'weak'}">
                <h4>${criterion.replace('_', ' ').toUpperCase()}</h4>
                <span class="status">${data.status}</span>
                <p class="score">Score: ${data.score}</p>
            </div>
        `;
    }
    html += '</div>';
    return html;
}

function generateEquitySection(equity) {
    return `
        <div class="element-grid">
            <div class="element-item">
                <h4>Overall Grade</h4>
                <span class="status">${equity.equity_grade}</span>
            </div>
            <div class="element-item">
                <h4>Justice40 Alignment</h4>
                <span class="status">${equity.justice40_alignment}</span>
            </div>
        </div>
    `;
}

function generateClimateSection(climate) {
    return `
        <div class="element-grid">
            <div class="element-item">
                <h4>Overall Grade</h4>
                <span class="status">${climate.climate_grade}</span>
            </div>
        </div>
    `;
}

function generateRiskSection(risk) {
    return `
        <div class="element-grid">
            <div class="element-item">
                <h4>Risk Quantification Score</h4>
                <span class="status">${risk.risk_quantification_score}%</span>
            </div>
        </div>
    `;
}

function generateFindingsList(findings) {
    let html = '';
    for (const finding of findings) {
        html += `
            <div class="finding-item ${finding.severity.toLowerCase()}">
                <div class="finding-header">
                    <span class="finding-severity ${finding.severity.toLowerCase()}">${finding.severity}</span>
                    <span class="finding-category">${finding.category}</span>
                </div>
                <div class="finding-description">${finding.finding}</div>
                <div class="finding-remediation">
                    <strong>FEMA Action:</strong> ${finding.fema_action}<br>
                    <strong>Remediation:</strong> ${finding.remediation}
                </div>
            </div>
        `;
    }
    return html;
}

function generateRecommendations(recommendations) {
    let html = '';
    const sections = {
        'immediate':   'Immediate Actions (0–30 days)',
        'near_term':   'Near-Term Actions (30–90 days)',
        'medium_term': 'Medium-Term Actions (3–6 months)',
        'long_term':   'Long-Term Actions (Next Update Cycle)'
    };
    for (const [section, title] of Object.entries(sections)) {
        if (recommendations[section]?.length > 0) {
            html += `<div class="recommendation-block"><h4>${title}</h4>`;
            for (const rec of recommendations[section]) {
                html += `
                    <div class="recommendation-item">
                        <span class="priority-tag ${rec.priority?.toLowerCase()}">${rec.priority}</span>
                        <div>
                            <strong>${rec.action}</strong>
                            <p style="font-size:0.9rem;color:var(--text-secondary)">${rec.details || ''}</p>
                        </div>
                    </div>
                `;
            }
            html += '</div>';
        }
    }
    return html || '<p>No specific recommendations.</p>';
}

function exportResults() {
    if (!currentResults) return;
    const blob = new Blob([JSON.stringify(currentResults, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `HMPSentinel_Report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}
