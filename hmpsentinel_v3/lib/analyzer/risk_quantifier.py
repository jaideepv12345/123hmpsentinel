# api/analyzer/risk_quantifier.py
"""
Risk Quantifier
Analyzes and quantifies hazard exposure, risk metrics, and vulnerability data
"""

import re
from typing import Dict, List, Any


class RiskQuantifier:
    """
    Quantifies risk from hazard mitigation plans.
    Identifies exposure metrics, critical facilities, and vulnerability data.
    """
    
    def __init__(self):
        pass
    
    def analyze(self, text: str, county_name: str, state: str) -> Dict:
        """
        Analyze plan for risk quantification
        Returns exposure metrics and vulnerability assessment
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        results = {
            'risk_quantification_score': 0,
            'exposure_metrics': {},
            'hazard_analysis': {},
            'critical_facilities': {},
            'vulnerable_populations': {},
            'data_currency': {},
            'gaps': [],
            'recommendations': []
        }
        
        # Analyze exposure metrics
        results['exposure_metrics'] = self._analyze_exposure(text_lower, word_count)
        
        # Analyze hazard-specific risks
        results['hazard_analysis'] = self._analyze_hazards(text_lower, word_count)
        
        # Analyze critical facilities
        results['critical_facilities'] = self._analyze_critical_facilities(text_lower)
        
        # Analyze vulnerable populations
        results['vulnerable_populations'] = self._analyze_vulnerable_populations(text_lower)
        
        # Assess data currency
        results['data_currency'] = self._assess_data_currency(text_lower)
        
        # Calculate overall risk quantification score
        results['risk_quantification_score'] = self._calculate_risk_score(results)
        
        # Identify gaps
        results['gaps'] = self._identify_gaps(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_exposure(self, text: str, word_count: int) -> Dict:
        """Analyze exposure metrics in the plan"""
        
        exposure_indicators = {
            'population': ['population', 'resident', 'people', 'pop', 'census', 'household'],
            'structures': ['structure', 'building', 'home', 'property', 'unit', 'parcel'],
            'critical_facilities': ['critical facility', 'essential facility', 'key facility', 'infrastructure'],
            'land_area': ['acre', 'square mile', 'sq mi', 'hectare', 'land', 'area'],
            'value': ['value', 'dollar', 'cost', 'loss', 'damage', 'estimate', 'exposure']
        }
        
        exposure_analysis = {}
        
        for category, indicators in exposure_indicators.items():
            matches = [ind for ind in indicators if ind in text]
            
            # Look for numeric patterns (e.g., 10,000 population, $500 million)
            numeric_patterns = self._extract_numeric_data(text, category)
            
            exposure_analysis[category] = {
                'indicators_present': len(matches),
                'indicators': matches,
                'numeric_data_found': len(numeric_patterns) > 0,
                'data_samples': numeric_patterns[:5],
                'status': 'Quantified' if len(numeric_patterns) > 2 else 'Partial' if len(numeric_patterns) > 0 else 'Not Quantified'
            }
        
        return exposure_analysis
    
    def _extract_numeric_data(self, text: str, category: str) -> List[str]:
        """Extract numeric data related to category"""
        
        patterns = {
            'population': r'\b\d{1,3}(?:,\d{3})+\b\s*(?:people|residents|pop|population)',
            'structures': r'\b\d{1,3}(?:,\d{3})+\b\s*(?:structure|building|home|unit)',
            'value': r'\$\d+(?:\.\d+)?\s*(?:million|billion|M|B)',
            'land': r'\b\d{1,3}(?:,\d{3})+\b\s*(?:acre|sq\s*mi|hectare)'
        }
        
        if category not in patterns:
            return []
        
        matches = re.findall(patterns[category], text, re.IGNORECASE)
        return matches[:5]
    
    def _analyze_hazards(self, text: str, word_count: int) -> Dict:
        """Analyze hazard-specific risk information"""
        
        hazard_definitions = {
            'flooding': {
                'keywords': ['flood', 'flooding', 'flash flood', 'river flood', 'coastal flood'],
                'metrics': ['flood zone', '100-year', '500-year', 'sfha', 'a zone', 'v zone'],
                'has_data': False
            },
            'hurricane': {
                'keywords': ['hurricane', 'tropical storm', 'typhoon', 'cyclone'],
                'metrics': ['category', 'saffir-simpson', 'wind speed', 'storm surge'],
                'has_data': False
            },
            'tornado': {
                'keywords': ['tornado', 'wind', 'twister'],
                'metrics': ['ef scale', 'ef0', 'ef1', 'wind speed', 'path'],
                'has_data': False
            },
            'wildfire': {
                'keywords': ['wildfire', 'fire', 'forest fire', 'brush fire'],
                'metrics': ['wui', 'wildland urban interface', 'fire risk', 'fuel model'],
                'has_data': False
            },
            'winter_storm': {
                'keywords': ['winter storm', 'snow', 'ice', 'blizzard', 'freezing'],
                'metrics': ['snow fall', 'ice accumulation', 'wind chill'],
                'has_data': False
            },
            'heat': {
                'keywords': ['heat', 'extreme heat', 'heat wave', 'high temperature'],
                'metrics': ['heat index', 'temperature', 'cooling center'],
                'has_data': False
            },
            'drought': {
                'keywords': ['drought', 'dry', 'arid'],
                'metrics': ['palmer', 'drought index', 'precipitation deficit'],
                'has_data': False
            },
            'earthquake': {
                'keywords': ['earthquake', 'seismic', 'quake'],
                'metrics': ['magnitude', 'richter', 'peak ground acceleration'],
                'has_data': False
            },
            'hazmat': {
                'keywords': ['hazmat', 'hazardous material', 'chemical', 'spill'],
                'metrics': ['facility', 'threshold', 'container'],
                'has_data': False
            },
            'dam_failure': {
                'keywords': ['dam', 'dam failure', 'levee', 'breach'],
                'metrics': ['failure mode', 'inundation zone', 'emergency action plan'],
                'has_data': False
            }
        }
        
        hazard_analysis = {}
        
        for hazard_name, hazard_data in hazard_definitions.items():
            # Check for keywords
            keyword_matches = sum(1 for kw in hazard_data['keywords'] if kw in text)
            
            # Check for metrics
            metric_matches = sum(1 for metric in hazard_data['metrics'] if metric in text)
            
            hazard_analysis[hazard_name] = {
                'keywords_found': keyword_matches,
                'metrics_found': metric_matches,
                'has_risk_data': keyword_matches >= 1 and metric_matches >= 1,
                'status': 'Analyzed' if keyword_matches >= 2 else 'Mentioned' if keyword_matches >= 1 else 'Not Addressed'
            }
        
        return hazard_analysis
    
    def _analyze_critical_facilities(self, text: str) -> Dict:
        """Analyze critical facility identification"""
        
        critical_facility_types = {
            'emergency_services': ['fire station', 'police', 'ems', 'emergency service', 'first responder'],
            'medical': ['hospital', 'medical', 'clinic', 'health', 'nursing', 'care facility'],
            'government': ['government', 'courthouse', 'city hall', 'county', 'administration'],
            'education': ['school', 'university', 'college', 'academy', 'education'],
            'infrastructure': ['water', 'sewer', 'power', 'electric', 'gas', 'telecom', 'transportation'],
            'shelter': ['shelter', 'evacuation', 'emergency shelter', 'warming center', 'cooling center']
        }
        
        cf_analysis = {}
        
        for cf_type, indicators in critical_facility_types.items():
            matches = [ind for ind in indicators if ind in text]
            
            cf_analysis[cf_type] = {
                'indicators_found': len(matches),
                'indicators': matches,
                'addressed': len(matches) > 0,
                'detail_level': 'Detailed' if len(matches) >= 2 else 'Basic' if len(matches) >= 1 else 'Not Addressed'
            }
        
        # Check for facility count/data
        facility_count = re.findall(r'\b\d+\b\s*(?:facility|facilities|critical facility)', text, re.IGNORECASE)
        
        cf_analysis['_summary'] = {
            'categories_addressed': sum(1 for cf in cf_analysis.values() if cf.get('addressed', False)),
            'total_categories': len(critical_facility_types),
            'has_count_data': len(facility_count) > 0
        }
        
        return cf_analysis
    
    def _analyze_vulnerable_populations(self, text: str) -> Dict:
        """Analyze vulnerable population identification"""
        
        vulnerable_groups = {
            'elderly': ['elderly', 'senior', 'older adult', 'age 65', 'aging'],
            'children': ['child', 'children', 'youth', 'school-age', 'infant'],
            'disabled': ['disabled', 'disability', 'handicap', 'special need', 'functional limitation'],
            'low_income': ['low income', 'poverty', 'poor', 'economically disadvantaged', 'below poverty'],
            'minority': ['minority', 'race', 'ethnic', 'language', 'immigrant', 'refugee'],
            'homeless': ['homeless', 'housing insecure', 'unhoused'],
            'medical_vulnerable': ['medical', 'health condition', 'chronically ill', 'medication'],
            'institutional': ['institutional', 'prison', 'jail', 'nursing home', 'group home']
        }
        
        vp_analysis = {}
        
        for group, indicators in vulnerable_groups.items():
            matches = [ind for ind in indicators if ind in text]
            
            vp_analysis[group] = {
                'indicators_found': len(matches),
                'indicators': matches,
                'addressed': len(matches) > 0
            }
        
        return vp_analysis
    
    def _assess_data_currency(self, text: str) -> Dict:
        """Assess data currency and freshness"""
        
        # Find year references
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        years = sorted(list(set(int(y) for y in years if int(y) <= 2030)))
        
        # Check for recent data
        recent_years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026']
        has_recent = any(y in text for y in recent_years)
        
        return {
            'years_referenced': years[-10:] if years else [],  # Last 10 years referenced
            'most_recent_year': max(years) if years else None,
            'data_age': ('Current' if (2026 - max(years)) <= 5 else 'Outdated') if years else 'Unknown',
            'has_recent_data': has_recent
        }
    
    def _calculate_risk_score(self, results: Dict) -> float:
        """Calculate overall risk quantification score"""
        
        # Score components
        exposure_score = 0
        exposure_metrics = results.get('exposure_metrics', {})
        quantified_count = sum(1 for m in exposure_metrics.values() if m.get('status') == 'Quantified')
        exposure_score = (quantified_count / len(exposure_metrics)) * 100 if exposure_metrics else 0
        
        # Hazard analysis score
        hazard_score = 0
        hazard_analysis = results.get('hazard_analysis', {})
        analyzed_count = sum(1 for h in hazard_analysis.values() if h.get('status') in ['Analyzed', 'Mentioned'])
        hazard_score = (analyzed_count / len(hazard_analysis)) * 100 if hazard_analysis else 0
        
        # Critical facilities score
        cf_score = 0
        critical_facilities = results.get('critical_facilities', {})
        summary = critical_facilities.get('_summary', {})
        cf_score = (summary.get('categories_addressed', 0) / summary.get('total_categories', 1)) * 100
        
        # Weighted average
        risk_score = (exposure_score * 0.4) + (hazard_score * 0.3) + (cf_score * 0.3)
        
        return round(risk_score, 1)
    
    def _identify_gaps(self, results: Dict) -> List[Dict]:
        """Identify risk quantification gaps"""
        
        gaps = []
        
        # Check exposure metrics
        exposure = results.get('exposure_metrics', {})
        for category, data in exposure.items():
            if data.get('status') == 'Not Quantified':
                gaps.append({
                    'category': 'exposure',
                    'gap': f"No numeric quantification for {category}",
                    'recommendation': f"Add quantified {category} data from census, assessor, or modeling"
                })
        
        # Check hazard analysis
        hazard_analysis = results.get('hazard_analysis', {})
        for hazard, data in hazard_analysis.items():
            if data.get('status') == 'Not Addressed':
                gaps.append({
                    'category': 'hazard',
                    'gap': f"Hazard {hazard} not adequately profiled",
                    'recommendation': f"Add risk profile for {hazard}"
                })
        
        # Check critical facilities
        critical = results.get('critical_facilities', {})
        summary = critical.get('_summary', {})
        if summary.get('categories_addressed', 0) < 4:
            gaps.append({
                'category': 'critical_facilities',
                'gap': "Incomplete critical facility identification",
                'recommendation': "Add comprehensive critical facility inventory"
            })
        
        return gaps
    
    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate risk quantification recommendations"""
        
        recommendations = []
        
        # Based on gaps
        for gap in results.get('gaps', []):
            recommendations.append({
                'priority': 'HIGH',
                'category': gap.get('category', 'unknown'),
                'action': 'Add risk quantification data',
                'details': gap.get('recommendation', 'Address data gaps')
            })
        
        # General recommendations
        if results.get('risk_quantification_score', 0) < 60:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'overall',
                'action': 'Strengthen overall risk quantification',
                'details': 'Add numeric exposure data, hazard-specific metrics, and critical facility inventory'
            })
        
        return recommendations
