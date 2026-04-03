# api/analyzer/climate_analysis.py
"""
Climate Foresight Analyzer
Evaluates climate change integration, future scenarios, and long-term resilience
"""

import re
from typing import Dict, List, Any


class ClimateAnalyzer:
    """
    Analyzes hazard mitigation plans for climate change integration and future-focused resilience.
    Evaluates climate scenarios, time horizons, compound hazards, and adaptation strategies.
    """
    
    def __init__(self):
        self.climate_framework = self._build_climate_matrix()
    
    def _build_climate_matrix(self) -> Dict:
        """Build climate evaluation matrix"""
        
        return {
            'climate_change_reference': {
                'name': 'Climate Change Reference',
                'description': 'Explicit mention of climate change in the plan',
                'indicators': [
                    'climate change', 'climate', 'warming', 'global warming',
                    'greenhouse', 'carbon', 'co2', 'emission', 'climate crisis',
                    'climate emergency'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should explicitly reference climate change'
            },
            'future_scenarios': {
                'name': 'Future Scenarios',
                'description': 'Projection of future conditions and risks',
                'indicators': [
                    'future', 'projection', 'scenario', 'model', 'predict',
                    'forecast', 'estimate', '2030', '2050', '2100', 'mid-century',
                    'end of century', 'coming decades'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should include future risk projections'
            },
            'sea_level_rise': {
                'name': 'Sea Level Rise (for coastal plans)',
                'description': 'Sea level rise analysis and integration',
                'indicators': [
                    'sea level', 'slr', 'sea-level rise', 'tide', 'surging',
                    'high tide', 'inundation', 'coastal', 'shoreline', 'erosion',
                    'nuisance flood', 'tideline'
                ],
                'threshold': 2,
                'fema_expectation': 'Coastal plans should include SLR analysis'
            },
            'temperature_change': {
                'name': 'Temperature Change',
                'description': 'Temperature projection and heat risk analysis',
                'indicators': [
                    'temperature', 'heat', 'warming', 'extreme heat',
                    'heat wave', 'cooling', 'degree day', 'warming scenario',
                    'hotter', 'record temperature'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should address temperature changes'
            },
            'precipitation_change': {
                'name': 'Precipitation Change',
                'description': 'Precipitation pattern changes and flood risk',
                'indicators': [
                    'precipitation', 'rainfall', 'intensity', 'extreme rain',
                    'heavy rain', 'storm event', 'flooding', 'drought',
                    'dry', 'wet', 'variability'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should address changing precipitation'
            },
            'compound_hazards': {
                'name': 'Compound Hazards',
                'description': 'Analysis of combined and cascading hazard impacts',
                'indicators': [
                    'compound', 'cascade', 'concurrent', 'multiple hazard',
                    'interaction', 'combined', 'sequence', 'chain', 'ripple',
                    'secondary', 'indirect'
                ],
                'threshold': 2,
                'fema_expectation': 'Plan should analyze compound hazard scenarios'
            },
            'adaptation_strategy': {
                'name': 'Adaptation Strategy',
                'description': 'Climate adaptation and resilience strategies',
                'indicators': [
                    'adapt', 'adaptation', 'resilient', 'resilience',
                    'adjust', 'modification', 'strategy', 'measure',
                    'intervention', 'response', 'prepare'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should include adaptation strategies'
            },
            'time_horizon': {
                'name': 'Time Horizon',
                'description': 'Explicit planning time horizon and temporal analysis',
                'indicators': [
                    'year', 'horizon', 'planning period', 'timeline',
                    'decade', '20-year', '30-year', '50-year', '100-year'
                ],
                'threshold': 3,
                'fema_expectation': 'Plan should specify planning time horizon'
            }
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze plan for climate foresight and future resilience
        Returns detailed climate scoring and gap analysis
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        results = {
            'climate_score': 0,
            'climate_grade': 'Unknown',
            'component_scores': {},
            'temporal_analysis': {},
            'hazard_climate_integration': {},
            'gaps': [],
            'strengths': [],
            'recommendations': []
        }
        
        # Evaluate each climate component
        for component_id, config in self.climate_framework.items():
            component_result = self._evaluate_component(
                text_lower, 
                config, 
                word_count
            )
            results['component_scores'][component_id] = component_result
        
        # Calculate overall climate score
        total_score = sum(
            score_data['score'] 
            for score_data in results['component_scores'].values()
        )
        max_possible = len(self.climate_framework) * 100
        results['climate_score'] = round((total_score / max_possible) * 100, 1)
        
        # Determine grade
        results['climate_grade'] = self._get_grade(results['climate_score'])
        
        # Temporal analysis
        results['temporal_analysis'] = self._analyze_temporal(text_lower)
        
        # Hazard-climate integration
        results['hazard_climate_integration'] = self._analyze_hazard_climate(text_lower)
        
        # Identify gaps and strengths
        results['gaps'] = self._identify_gaps(results['component_scores'])
        results['strengths'] = self._identify_strengths(results['component_scores'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(
            results['component_scores'],
            results['temporal_analysis']
        )
        
        return results
    
    def _evaluate_component(self, text: str, config: Dict, word_count: int) -> Dict:
        """Evaluate a single climate component"""
        
        indicator_matches = []
        for indicator in config['indicators']:
            if indicator in text:
                indicator_matches.append(indicator)
        
        unique_matches = len(set(indicator_matches))
        
        # Calculate score
        if unique_matches >= config['threshold']:
            status = 'Well Addressed'
            score = min(100, 60 + (unique_matches - config['threshold']) * 15)
        elif unique_matches >= 1:
            status = 'Partial'
            score = 30 + (unique_matches * 15)
        else:
            status = 'Not Addressed'
            score = max(10, unique_matches * 10)
        
        return {
            'name': config['name'],
            'status': status,
            'score': round(score, 1),
            'unique_indicators': unique_matches,
            'indicators_found': list(set(indicator_matches))[:10],
            'fema_expectation': config['fema_expectation']
        }
    
    def _analyze_temporal(self, text: str) -> Dict:
        """Analyze temporal aspects and time horizons"""
        
        # Find year references
        year_pattern = r'\b(19|20)\d{2}\b'
        years_found = re.findall(year_pattern, text)
        
        # Identify specific time horizons
        time_indicators = {
            'short_term': ['5-year', '5 year', 'near-term', 'near term'],
            'medium_term': ['10-year', '10 year', '20-year', '20 year', 'mid-century'],
            'long_term': ['50-year', '50 year', '100-year', '100 year', 'century', '2100']
        }
        
        temporal_analysis = {
            'years_referenced': list(set(years_found))[:20],
            'has_time_horizon': False,
            'time_horizons_found': []
        }
        
        for horizon, indicators in time_indicators.items():
            if any(ind in text for ind in indicators):
                temporal_analysis['has_time_horizon'] = True
                temporal_analysis['time_horizons_found'].append(horizon)
        
        return temporal_analysis
    
    def _analyze_hazard_climate(self, text: str) -> Dict:
        """Analyze how specific hazards are integrated with climate"""
        
        hazard_climate_pairs = {
            'flooding': ['climate change', 'future', 'precipitation', 'intensity', 'extreme'],
            'hurricane': ['climate change', 'intensity', 'sea surface', 'warm', 'category'],
            'wildfire': ['climate', 'drought', 'warming', 'drying', 'fire season'],
            'heat': ['climate change', 'warming', 'extreme heat', 'temperature'],
            'drought': ['climate change', 'precipitation', 'warming', 'dry']
        }
        
        integration_analysis = {}
        
        for hazard, climate_terms in hazard_climate_pairs.items():
            integration_score = sum(1 for term in climate_terms if term in text)
            integration_analysis[hazard] = {
                'climate_integrated': integration_score > 0,
                'integration_depth': integration_score,
                'status': 'Integrated' if integration_score >= 2 else 'Partial' if integration_score >= 1 else 'Not Integrated'
            }
        
        return integration_analysis
    
    def _identify_gaps(self, component_scores: Dict) -> List[Dict]:
        """Identify climate gaps"""
        
        gaps = []
        priority_components = ['future_scenarios', 'compound_hazards', 'adaptation_strategy']
        
        for component_id, score_data in component_scores.items():
            if score_data['status'] != 'Well Addressed':
                gaps.append({
                    'component': component_id,
                    'name': score_data['name'],
                    'status': score_data['status'],
                    'description': f"{score_data['name']} is {score_data['status'].lower()}",
                    'priority': 'HIGH' if component_id in priority_components else 'MEDIUM',
                    'recommendation': score_data['fema_expectation']
                })
        
        return gaps
    
    def _identify_strengths(self, component_scores: Dict) -> List[Dict]:
        """Identify climate strengths"""
        
        strengths = []
        for component_id, score_data in component_scores.items():
            if score_data['status'] == 'Well Addressed':
                strengths.append({
                    'component': component_id,
                    'name': score_data['name'],
                    'description': f"{score_data['name']} is adequately addressed",
                    'indicators': score_data['indicators_found']
                })
        
        return strengths
    
    def _generate_recommendations(self, component_scores: Dict, temporal_analysis: Dict) -> List[Dict]:
        """Generate climate recommendations"""
        
        recommendations = []
        
        # Future scenarios
        if component_scores.get('future_scenarios', {}).get('status') != 'Well Addressed':
            recommendations.append({
                'priority': 'HIGH',
                'component': 'future_scenarios',
                'action': 'Add future scenario analysis',
                'details': 'Include climate projections for 2030, 2050, and 2100 time horizons'
            })
        
        # Compound hazards
        if component_scores.get('compound_hazards', {}).get('status') != 'Well Addressed':
            recommendations.append({
                'priority': 'HIGH',
                'component': 'compound_hazards',
                'action': 'Add compound hazard analysis',
                'details': 'Include analysis of cascading and concurrent hazard impacts'
            })
        
        # Adaptation strategy
        if component_scores.get('adaptation_strategy', {}).get('status') != 'Well Addressed':
            recommendations.append({
                'priority': 'MEDIUM',
                'component': 'adaptation_strategy',
                'action': 'Strengthen adaptation strategies',
                'details': 'Add specific climate adaptation measures and implementation timeline'
            })
        
        # Time horizon
        if not temporal_analysis.get('has_time_horizon', False):
            recommendations.append({
                'priority': 'MEDIUM',
                'component': 'time_horizon',
                'action': 'Define explicit planning time horizon',
                'details': 'Specify planning period (e.g., 20-year, 50-year) for risk assessment'
            })
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        
        if score >= 80:
            return 'A - Strong Climate Foresight'
        elif score >= 70:
            return 'B - Adequate Climate Integration'
        elif score >= 60:
            return 'C - Partial Climate Elements'
        elif score >= 50:
            return 'D - Limited Climate Components'
        else:
            return 'F - Missing Climate Framework'
