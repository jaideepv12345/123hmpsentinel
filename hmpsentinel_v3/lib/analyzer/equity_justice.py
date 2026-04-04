# api/analyzer/equity_justice.py
"""
Equity and Justice40 Compliance Analyzer
Evaluates plan alignment with Justice40, CEJST, and equitable resilience requirements
"""

import re
from typing import Dict, List, Any


class EquityJusticeAnalyzer:
    """
    Analyzes hazard mitigation plans for equity and environmental justice compliance.
    Evaluates Justice40 initiative alignment, CEJST integration, and disadvantaged community focus.
    """
    
    def __init__(self):
        self.equity_framework = self._build_equity_matrix()
    
    def _build_equity_matrix(self) -> Dict:
        """Build equity evaluation matrix"""
        
        return {
            'cejst_integration': {
                'name': 'CEJST Data Integration',
                'description': 'Climate and Economic Justice Screening Tool data usage',
                'indicators': [
                    'cejst', 'climate and economic justice', 'justice40',
                    'screening tool', 'disadvantaged community', 'DAC',
                    'burdened community', 'overburdened community'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should reference CEJST data to identify disadvantaged communities'
            },
            'social_vulnerability': {
                'name': 'Social Vulnerability Integration',
                'description': 'Social Vulnerability Index (SVI) and demographic analysis',
                'indicators': [
                    'svi', 'social vulnerability', 'vulnerable population',
                    'demographic', 'census', 'income', 'poverty', 'minority',
                    'race', 'ethnicity', 'language', 'age', 'disability',
                    'transportation', 'mobile home', 'manufactured housing'
                ],
                'threshold': 5,
                'fema_expectation': 'Plan should include SVI-based vulnerability analysis'
            },
            'environmental_justice': {
                'name': 'Environmental Justice',
                'description': 'Environmental justice considerations and analysis',
                'indicators': [
                    'environmental justice', 'EJ', 'pollution', 'contamination',
                    'brownfield', 'superfund', 'waste', 'industrial', 'air quality',
                    'water quality', 'toxic', 'hazardous facility'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should address environmental justice communities'
            },
            'community_engagement': {
                'name': 'Community Engagement',
                'description': 'Engagement with vulnerable and disadvantaged communities',
                'indicators': [
                    'outreach', 'engagement', 'public meeting', 'stakeholder',
                    'community input', 'focus group', 'survey', 'interview',
                    'tribal', 'indigenous', 'language access', 'lep',
                    'limited english', 'translation', 'accessibility', 'ada'
                ],
                'threshold': 4,
                'fema_expectation': 'Plan should document engagement with disadvantaged communities'
            },
            'equitable_benefits': {
                'name': 'Equitable Benefit Distribution',
                'description': 'Analysis of how mitigation benefits are distributed',
                'indicators': [
                    'benefit distribution', 'equitable', 'priority', 'vulnerable',
                    'underserved', 'historically marginalized', 'persistent poverty',
                    'low-income', 'disadvantage', 'frontline'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should demonstrate how benefits reach disadvantaged communities'
            },
            'language_access': {
                'name': 'Language Access / LEP',
                'description': 'Limited English Proficiency and multilingual services',
                'indicators': [
                    'lep', 'limited english', 'non-english', 'spanish', 'language',
                    'translation', 'multilingual', 'interpreter', 'vietnamese',
                    'chinese', 'korean', 'other language'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should address LEP population needs'
            },
            'accessibility': {
                'name': 'Accessibility / ADA',
                'description': 'Americans with Disabilities Act compliance',
                'indicators': [
                    'ada', 'accessibility', 'disabled', 'disability', 'handicap',
                    'wheelchair', 'mobility', 'special need', 'functional need'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should address accessibility for people with disabilities'
            },
            'transportation_disadvantaged': {
                'name': 'Transportation Disadvantaged',
                'description': 'Transportation vulnerability considerations',
                'indicators': [
                    'transportation', 'transit', 'transport', 'car', 'vehicle',
                    'mobility', 'rural', 'remote', 'unserved', 'public transit'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should consider transportation-disadvantaged populations'
            }
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze plan for equity and Justice40 compliance
        Returns detailed equity scoring and gap analysis
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        results = {
            'equity_score': 0,
            'equity_grade': 'Unknown',
            'justice40_alignment': 'Unknown',
            'component_scores': {},
            'cejst_assessment': {},
            'svi_assessment': {},
            'gaps': [],
            'strengths': [],
            'recommendations': []
        }
        
        # Evaluate each equity component
        for component_id, config in self.equity_framework.items():
            component_result = self._evaluate_component(
                text_lower, 
                config, 
                word_count
            )
            results['component_scores'][component_id] = component_result
        
        # Calculate overall equity score
        total_score = sum(
            score_data['score'] 
            for score_data in results['component_scores'].values()
        )
        max_possible = len(self.equity_framework) * 100
        results['equity_score'] = round((total_score / max_possible) * 100, 1)
        
        # Determine grade
        results['equity_grade'] = self._get_grade(results['equity_score'])
        
        # Assess Justice40 alignment
        results['justice40_alignment'] = self._assess_justice40(results['component_scores'])
        
        # CEJST assessment
        results['cejst_assessment'] = self._assess_cejst(text_lower)
        
        # SVI assessment
        results['svi_assessment'] = self._assess_svi(text_lower)
        
        # Identify gaps and strengths
        results['gaps'] = self._identify_gaps(results['component_scores'])
        results['strengths'] = self._identify_strengths(results['component_scores'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(
            results['component_scores'],
            results['justice40_alignment']
        )
        
        return results
    
    def _evaluate_component(self, text: str, config: Dict, word_count: int) -> Dict:
        """Evaluate a single equity component"""
        
        indicator_matches = []
        for indicator in config['indicators']:
            if indicator in text:
                indicator_matches.append(indicator)
        
        unique_matches = len(set(indicator_matches))
        
        # Calculate score
        if unique_matches >= config['threshold']:
            status = 'Present'
            score = min(100, 60 + (unique_matches - config['threshold']) * 10)
        elif unique_matches >= 1:
            status = 'Partial'
            score = 30 + (unique_matches * 15)
        else:
            status = 'Missing'
            score = max(10, unique_matches * 10)
        
        return {
            'name': config['name'],
            'status': status,
            'score': round(score, 1),
            'unique_indicators': unique_matches,
            'indicators_found': list(set(indicator_matches))[:10],
            'fema_expectation': config['fema_expectation']
        }
    
    def _assess_justice40(self, component_scores: Dict) -> str:
        """Assess Justice40 alignment"""
        
        # Justice40 requires CEJST, SVI, and equitable benefits
        justice40_indicators = [
            'cejst_integration',
            'social_vulnerability',
            'equitable_benefits'
        ]
        
        present_count = sum(
            1 for indicator in justice40_indicators 
            if component_scores.get(indicator, {}).get('status') == 'Present'
        )
        
        if present_count >= 3:
            return 'Aligned - Strong Justice40 alignment'
        elif present_count >= 2:
            return 'Partial - Moderate Justice40 alignment'
        elif present_count >= 1:
            return 'Limited - Weak Justice40 alignment'
        else:
            return 'Not Aligned - No clear Justice40 alignment'
    
    def _assess_cejst(self, text: str) -> Dict:
        """Assess CEJST integration"""
        
        cejst_indicators = ['cejst', 'climate and economic justice', 'justice40', 
                          'screening tool', 'disadvantaged community']
        
        matches = sum(1 for ind in cejst_indicators if ind in text)
        
        return {
            'cejst_referenced': matches > 0,
            'indicators_found': matches,
            'recommendation': 'Add explicit CEJST data reference if not present' if matches == 0 else 'CEJST data referenced'
        }
    
    def _assess_svi(self, text: str) -> Dict:
        """Assess SVI integration"""
        
        svi_indicators = ['svi', 'social vulnerability index', 'social vulnerability', 
                        'census tract', 'demographic', 'vulnerable population']
        
        matches = sum(1 for ind in svi_indicators if ind in text)
        
        return {
            'svi_referenced': matches > 0,
            'indicators_found': matches,
            'recommendation': 'Add SVI reference and mapping if not present' if matches == 0 else 'SVI data referenced'
        }
    
    def _identify_gaps(self, component_scores: Dict) -> List[Dict]:
        """Identify equity gaps"""
        
        gaps = []
        for component_id, score_data in component_scores.items():
            if score_data['status'] != 'Present':
                gaps.append({
                    'component': component_id,
                    'name': score_data['name'],
                    'status': score_data['status'],
                    'description': f"{score_data['name']} is {score_data['status'].lower()}",
                    'recommendation': score_data['fema_expectation']
                })
        
        return gaps
    
    def _identify_strengths(self, component_scores: Dict) -> List[Dict]:
        """Identify equity strengths"""
        
        strengths = []
        for component_id, score_data in component_scores.items():
            if score_data['status'] == 'Present':
                strengths.append({
                    'component': component_id,
                    'name': score_data['name'],
                    'description': f"{score_data['name']} is adequately addressed",
                    'indicators': score_data['indicators_found']
                })
        
        return strengths
    
    def _generate_recommendations(self, component_scores: Dict, justice40_alignment: str) -> List[Dict]:
        """Generate equity recommendations"""
        
        recommendations = []
        
        # Priority recommendations based on gaps
        priority_gaps = ['cejst_integration', 'social_vulnerability', 'equitable_benefits']
        
        for gap in priority_gaps:
            score_data = component_scores.get(gap, {})
            if score_data.get('status') != 'Present':
                recommendations.append({
                    'priority': 'HIGH',
                    'component': gap,
                    'action': f"Add {score_data.get('name', gap)} components",
                    'details': score_data.get('fema_expectation', 'Required for Justice40 compliance')
                })
        
        # General recommendations
        if 'Partial' in justice40_alignment or 'Not Aligned' in justice40_alignment:
            recommendations.append({
                'priority': 'HIGH',
                'component': 'justice40',
                'action': 'Strengthen Justice40 alignment',
                'details': 'Add explicit CEJST, SVI, and equitable benefit distribution analysis'
            })
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        
        if score >= 80:
            return 'A - Strong Equity Framework'
        elif score >= 70:
            return 'B - Adequate Equity Integration'
        elif score >= 60:
            return 'C - Partial Equity Elements'
        elif score >= 50:
            return 'D - Limited Equity Components'
        else:
            return 'F - Missing Equity Framework'
