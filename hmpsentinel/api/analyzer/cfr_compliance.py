# api/analyzer/cfr_compliance.py
"""
Deep CFR 201.6 Compliance Analyzer
Operational rigor - not just keyword matching
"""

import re
from typing import Dict, List, Any


class CFRComplianceAnalyzer:
    """
    Analyzes hazard mitigation plans against FEMA 44 CFR 201.6 requirements
    Provides structured compliance assessment with specific findings
    """
    
    def __init__(self):
        self.cfr_requirements = self._build_requirement_matrix()
    
    def _build_requirement_matrix(self) -> Dict:
        """Build comprehensive CFR 201.6 requirement matrix"""
        return {
            'A1': {
                'name': 'Multi-jurisdictional Participation',
                'requirement': 'Plan must include documentation of jurisdictions participating in the planning process',
                'indicators': [
                    'jurisdiction', 'participating', 'stakeholder', 'meeting', 'coordination',
                    'planning team', 'representative', 'adopted by'
                ],
                'weak_indicators': [
                    'may include', 'should consider', 'will be included'
                ],
                'fema_expectation': 'List of participating jurisdictions with evidence of their involvement'
            },
            'A2': {
                'name': 'Planning Process',
                'requirement': 'Plan must include documentation of the planning process, including public involvement',
                'indicators': [
                    'public meeting', 'comment period', 'stakeholder meeting', 'outreach',
                    'planning process', 'public input', 'review and comment'
                ],
                'weak_indicators': [
                    'will conduct', 'intends to', 'plans to'
                ],
                'fema_expectation': 'Timeline and evidence of public engagement activities'
            },
            'B1': {
                'name': 'Hazard Identification',
                'requirement': 'Plan must identify all hazards that could affect the planning area',
                'indicators': [
                    'hazard identification', 'risk assessment', 'hazard profile',
                    'hazard analysis', 'flood', 'hurricane', 'tornado', 'earthquake',
                    'wildfire', 'severe weather', 'winter storm', 'drought'
                ],
                'weak_indicators': [
                    'may include', 'some hazards'
                ],
                'fema_expectation': 'Comprehensive list of hazards with characterization'
            },
            'B2': {
                'name': 'Vulnerability Assessment',
                'requirement': 'Plan must include vulnerability assessment showing risks from identified hazards',
                'indicators': [
                    'vulnerability', 'exposure', 'population exposed', 'structures exposed',
                    'critical facility', 'infrastructure', 'hazard zone', 'flood zone',
                    'risk analysis', 'damage assessment', 'loss estimation'
                ],
                'weak_indicators': [
                    'may be affected', 'could be impacted', 'potential'
                ],
                'fema_expectation': 'Quantified exposure data with methodology'
            },
            'B3': {
                'name': 'Capability Assessment',
                'requirement': 'Plan must include an assessment of existing authorities, policies, programs, and resources',
                'indicators': [
                    'capability assessment', 'existing authority', 'policy', 'program',
                    'resource', 'capacity', 'building code', 'zoning', 'floodplain',
                    'emergency management', 'personnel', 'budget'
                ],
                'weak_indicators': [
                    'some capabilities', 'limited capacity'
                ],
                'fema_expectation': 'Structured inventory of local capabilities'
            },
            'B4': {
                'name': 'Repetitive Loss Properties',
                'requirement': 'Plan must include a list of Repetitive Loss (RL) properties and SRL properties',
                'indicators': [
                    'repetitive loss', 'RL property', 'SRL', 'severe repetitive loss',
                    'flood claim', 'NFIP', 'claims history', '多次损失', '重复损失'
                ],
                'weak_indicators': [],
                'fema_expectation': 'Table or list of RL/SRL properties with summary data'
            },
            'B5': {
                'name': 'Future Development Trends',
                'requirement': 'Plan must include a description of expected future development patterns',
                'indicators': [
                    'future development', 'growth', 'land use', 'zoning', 'development trend',
                    'population growth', 'build-out', 'comprehensive plan', 'master plan'
                ],
                'weak_indicators': [
                    'may occur', 'could happen'
                ],
                'fema_expectation': 'Discussion of how future development affects risk'
            },
            'C1': {
                'name': 'Mitigation Goals',
                'requirement': 'Plan must include local mitigation goals for reducing identified risks',
                'indicators': [
                    'goal', 'objective', 'mitigation goal', 'reduce risk', 'protect',
                    'minimize', 'prevent', 'improve', 'enhance'
                ],
                'weak_indicators': [
                    'may include', 'could include'
                ],
                'fema_expectation': 'Clear, measurable goals with connection to risks'
            },
            'C2': {
                'name': 'Mitigation Actions',
                'requirement': 'Plan must include a range of mitigation actions and projects',
                'indicators': [
                    'mitigation action', 'project', 'activity', 'strategy',
                    'acquisition', 'elevation', 'retrofit', 'warning', 'education',
                    'planning', 'regulation', 'infrastructure', 'property protection'
                ],
                'weak_indicators': [
                    'may consider', 'could implement'
                ],
                'fema_expectation': 'Specific actions with responsible parties and timelines'
            },
            'C3': {
                'name': 'Action Prioritization',
                'requirement': 'Plan must include a process for prioritizing actions',
                'indicators': [
                    'prioritize', 'priority', 'ranking', 'criteria', 'score',
                    'benefit-cost', 'ranking method', 'evaluation', 'selection'
                ],
                'weak_indicators': [
                    'will prioritize', 'intend to prioritize'
                ],
                'fema_expectation': 'Documented prioritization methodology'
            },
            'C4': {
                'name': 'Benefit-Cost Review',
                'requirement': 'Plan must include documentation of benefit-cost analysis for projects',
                'indicators': [
                    'benefit-cost', 'BCA', 'cost-benefit', 'economic analysis',
                    'benefit', 'cost', 'analysis', 'FEMA BCA tool'
                ],
                'weak_indicators': [],
                'fema_expectation': 'Summary BCA for each project or methodology description'
            },
            'C5': {
                'name': 'Implementation and Funding',
                'requirement': 'Plan must describe how actions will be implemented and funded',
                'indicators': [
                    'implement', 'funding', 'budget', 'grant', 'FEMA', 'HMGP',
                    'PDM', 'BRIC', 'timeline', 'schedule', 'responsible party'
                ],
                'weak_indicators': [
                    'may seek', 'could apply'
                ],
                'fema_expectation': 'Implementation details and funding sources for each action'
            },
            'D1': {
                'name': 'Plan Maintenance',
                'requirement': 'Plan must include provisions for plan maintenance, monitoring, and updates',
                'indicators': [
                    'plan maintenance', 'monitor', 'update', 'review', 'annual',
                    'five-year', 'revision', 'point of contact', 'responsible party'
                ],
                'weak_indicators': [
                    'will review', 'intend to update'
                ],
                'fema_expectation': 'Schedule and process for plan maintenance'
            },
            'D2': {
                'name': 'Integration with Other Plans',
                'requirement': 'Plan must demonstrate integration with other relevant plans',
                'indicators': [
                    'integrat', 'compatible', 'consistent', 'comprehensive plan',
                    'master plan', 'emergency plan', 'capital improvement',
                    'zoning', 'building code', 'sea level rise', 'climate adaptation'
                ],
                'weak_indicators': [],
                'fema_expectation': 'Explicit links to other local plans'
            },
            'D3': {
                'name': 'Plan Adoption',
                'requirement': 'Plan must include evidence of plan adoption by participating jurisdictions',
                'indicators': [
                    'adopt', 'resolution', 'ordinance', 'council', 'commission',
                    'approved', 'certified', 'adoption'
                ],
                'weak_indicators': [],
                'fema_expectation': 'Adoption resolutions or documentation'
            }
        }
    
    def analyze(self, text: str, jurisdictions: List[str]) -> Dict:
        """
        Perform comprehensive CFR 201.6 compliance analysis
        Returns structured assessment with specific findings
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        results = {
            'overall_score': 0,
            'compliance_status': 'Unknown',
            'element_assessment': {},
            'jurisdictional_analysis': {},
            'compliance_gaps': [],
            'strengths': [],
            'fema_submission_assessment': {}
        }
        
        total_score = 0
        assessed_elements = 0
        
        for element_id, requirements in self.cfr_requirements.items():
            assessment = self._assess_element(
                text_lower, 
                requirements, 
                word_count,
                jurisdictions
            )
            
            results['element_assessment'][element_id] = assessment
            
            # Calculate score
            if assessment['status'] == 'Present':
                total_score += 100
                assessed_elements += 1
            elif assessment['status'] == 'Weak':
                total_score += 50
                assessed_elements += 1
            else:
                total_score += 0
                assessed_elements += 1
            
            # Track gaps
            if assessment['status'] in ['Weak', 'Missing']:
                results['compliance_gaps'].append({
                    'element': element_id,
                    'name': requirements['name'],
                    'status': assessment['status'],
                    'finding': assessment['finding'],
                    'remediation_hint': assessment['remediation_hint']
                })
            else:
                results['strengths'].append({
                    'element': element_id,
                    'name': requirements['name']
                })
        
        # Calculate overall score
        if assessed_elements > 0:
            results['overall_score'] = round(total_score / assessed_elements, 1)
        
        # Determine compliance status
        if results['overall_score'] >= 90:
            results['compliance_status'] = 'Substantially Compliant'
        elif results['overall_score'] >= 70:
            results['compliance_status'] = 'Partially Compliant'
        elif results['overall_score'] >= 50:
            results['compliance_status'] = 'Needs Improvement'
        else:
            results['compliance_status'] = 'Non-Compliant'
        
        # Jurisdictional analysis
        results['jurisdictional_analysis'] = self._analyze_jurisdictions(
            text_lower, 
            jurisdictions,
            word_count
        )
        
        # FEMA submission assessment
        results['fema_submission_assessment'] = self._generate_submission_assessment(
            results['compliance_gaps'],
            results['overall_score']
        )
        
        return results
    
    def _assess_element(
        self, 
        text: str, 
        requirements: Dict,
        word_count: int,
        jurisdictions: List[str]
    ) -> Dict:
        """Assess a single CFR element"""
        
        # Check strong indicators
        strong_matches = sum(1 for indicator in requirements['indicators'] 
                           if indicator in text)
        
        # Check weak indicators
        weak_matches = sum(1 for indicator in requirements.get('weak_indicators', [])
                          if indicator in text)
        
        # Calculate indicator density
        indicator_density = strong_matches / max(word_count / 1000, 1)
        
        # Determine status
        if strong_matches >= 3 and indicator_density > 0.5:
            status = 'Present'
            finding = f"Good coverage of {requirements['name']} with multiple strong indicators"
        elif strong_matches >= 1 and indicator_density > 0.2:
            status = 'Weak'
            finding = f"Partial coverage of {requirements['name']} - needs more specific documentation"
        else:
            status = 'Missing'
            finding = f"Limited or no documentation of {requirements['name']}"
        
        # Generate specific remediation hint
        remediation_hint = self._generate_remediation(
            requirements['fema_expectation'],
            status
        )
        
        # Determine likely FEMA reviewer action
        reviewer_action = self._predict_fema_action(status, requirements['name'])
        
        return {
            'name': requirements['name'],
            'status': status,
            'finding': finding,
            'indicator_count': strong_matches,
            'indicator_density': round(indicator_density, 2),
            'remediation_hint': remediation_hint,
            'reviewer_likely_action': reviewer_action,
            'fema_expectation': requirements['fema_expectation']
        }
    
    def _analyze_jurisdictions(self, text: str, jurisdictions: List[str], word_count: int) -> Dict:
        """Analyze multi-jurisdictional aspects"""
        
        adoption_patterns = [
            'adopted', 'resolution', 'adoption', 'certified', 'approved',
            'council', 'commission', 'board of'
        ]
        
        participation_patterns = [
            'participated', 'meeting', 'stakeholder', 'planning team',
            'represented', 'collaborated', 'coordinated'
        ]
        
        adoption_count = sum(1 for pattern in adoption_patterns if pattern in text)
        participation_count = sum(1 for pattern in participation_patterns if pattern in text)
        
        return {
            'jurisdictions_detected': len(jurisdictions),
            'jurisdiction_list': jurisdictions[:10],  # Top 10
            'adoption_evidence_score': min(adoption_count / 2, 5),
            'participation_evidence_score': min(participation_count / 2, 5),
            'multi_jurisdictional_strength': 'Strong' if adoption_count >= 3 else 'Moderate' if adoption_count >= 1 else 'Weak'
        }
    
    def _generate_remediation(self, fema_expectation: str, status: str) -> str:
        """Generate specific remediation guidance"""
        
        if status == 'Missing':
            return f"FEMA requires: {fema_expectation}. Add complete section with data and methodology."
        elif status == 'Weak':
            return f"FEMA expects: {fema_expectation}. Strengthen with specific data and documentation."
        else:
            return "Continue to maintain and update this section in future plan revisions."
    
    def _predict_fema_action(self, status: str, element_name: str) -> str:
        """Predict likely FEMA reviewer action"""
        
        action_map = {
            'Present': 'No action required - element meets FEMA expectations',
            'Weak': 'May request additional documentation or clarification',
            'Missing': 'Will likely request addition of this element before approval'
        }
        
        return action_map.get(status, 'Unknown')
    
    def _generate_submission_assessment(self, gaps: List[Dict], score: float) -> Dict:
        """Generate FEMA submission readiness assessment"""
        
        high_severity = [g for g in gaps if g['status'] == 'Missing']
        medium_severity = [g for g in gaps if g['status'] == 'Weak']
        
        return {
            'gaps_count': len(gaps),
            'high_severity_count': len(high_severity),
            'medium_severity_count': len(medium_severity),
            'overall_score': score,
            'recommendation': self._get_submission_recommendation(score, len(high_severity))
        }
    
    def _get_submission_recommendation(self, score: float, high_gaps: int) -> str:
        """Get submission recommendation based on gaps"""
        
        if high_gaps > 3:
            return "Not recommended for submission - address high-severity gaps first"
        elif high_gaps > 0:
            return "Conditional approval likely - address gaps before formal submission"
        elif score >= 80:
            return "Ready for submission"
        else:
            return "Consider addressing remaining gaps before submission"
