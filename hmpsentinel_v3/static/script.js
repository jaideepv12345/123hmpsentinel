// public/script.js
let currentResults = null;

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('file');
    
    formData.append('file', fileInput.files[0]);
    formData.append('county', document.getElementById('county').value);
    formData.append('state', document.getElementById('state').value);
    formData.append('plan_title', document.getElementById('plan_title').value);
    formData.append('plan_year', document.getElementById('plan_year').value);
    formData.append('plan_type', document.getElementById('plan_type').value);
    
    const btn = document.getElementById('analyzeBtn');
    btn.disabled = true;
    btn.querySelector('.btn-text').style.display = 'none';
    btn.querySelector('.btn-loading').style.display = 'inline';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        currentResults = data;
        displayResults(data);
        
    } catch (error) {
        document.getElementById('error').style.display = 'block';
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('results').style.display = 'none';
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').style.display = 'inline';
        btn.querySelector('.btn-loading').style.display = 'none';
    }
});

function displayResults(data) {
    document.getElementById('error').style.display = 'none';
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
    let html = `
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
    return html;
}

function generateClimateSection(climate) {
    let html = `
        <div class="element-grid">
            <div class="element-item">
                <h4>Overall Grade</h4>
                <span class="status">${climate.climate_grade}</span>
            </div>
        </div>
    `;
    return html;
}

function generateRiskSection(risk) {
    let html = `
        <div class="element-grid">
            <div class="element-item">
                <h4>Risk Quantification Score</h4>
                <span class="status">${risk.risk_quantification_score}%</span>
            </div>
        </div>
    `;
    return html;
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
        'immediate': 'Immediate Actions (0-30 days)',
        'near_term': 'Near-Term Actions (30-90 days)',
        'medium_term': 'Medium-Term Actions (3-6 months)',
        'long_term': 'Long-Term Actions (Next Update Cycle)'
    };
    
    for (const [section, title] of Object.entries(sections)) {
        if (recommendations[section] && recommendations[section].length > 0) {
            html += `<div class="recommendation-block"><h4>${title}</h4>`;
            for (const rec of recommendations[section]) {
                html += `
                    <div class="recommendation-item">
                        <span class="priority-tag ${rec.priority?.toLowerCase()}">${rec.priority}</span>
                        <div>
                            <strong>${rec.action}</strong>
                            <p style="font-size: 0.9rem; color: var(--text-secondary)">${rec.details || ''}</p>
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
    
    const blob = new Blob([JSON.stringify(currentResults, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `HMPSentinel_Report_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}
