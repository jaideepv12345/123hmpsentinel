# api/analyzer/bric_analysis.py
"""
BRIC (Building Resilient Infrastructure in Communities) Readiness Analyzer
Evaluates plan competitiveness for FEMA BRIC funding
"""

import re
from typing import Dict, List, Any


class BRICAnalyzer:
    """
    Analyzes hazard mitigation plans for BRIC (Building Resilient Infrastructure in Communities) 
    funding competitiveness. Evaluates innovation, climate, equity, and maintenance requirements.
    """
    
    def __init__(self):
        self.bric_criteria = self._build_bric_matrix()
    
    def _build_bric_matrix(self) -> Dict:
        """Build BRIC evaluation criteria matrix"""
        return {
            'innovation': {
                'weight': 0.25,
                'indicators': [
                    'nature-based', 'green infrastructure', 'innovative', 'novel',
                    'nature-based solutions', 'low-impact development', 'green roof',
                    'rain garden', 'bioswale', 'living shoreline', 'restore', 'ecological',
                    'natural system', 'engineered', 'advanced', 'cutting-edge'
                ],
                'fema_priority': 'FEMA values projects that use innovative approaches to reduce risk'
            },
            'climate': {
                'weight': 0.25,
                'indicators': [
                    'climate change', 'climate adaptation', 'future condition',
                    'sea level rise', 'changing climate', 'warming', 'greenhouse',
                    'carbon', 'resilience', 'scenario', 'projection', 'model',
                    'future risk', 'changing hazard', 'extreme weather', 'compound'
                ],
                'fema_priority': 'BRIC prioritizes projects that address future climate conditions'
            },
            'equity': {
                'weight': 0.25,
                'indicators': [
                    'vulnerable', 'underserved', 'disadvantaged', 'environmental justice',
                    'low-income', 'minority', 'overburdened', 'social vulnerability',
                    'SVI', 'EJ', 'DAC', 'frontline', 'underserved community',
                    'historically marginalized', 'persistent poverty'
                ],
                'fema_priority': 'Justice40 initiative requires benefits to disadvantaged communities'
            },
            'maintenance': {
                'weight': 0.25,
                'indicators': [
                    'maintenance', 'operation', 'O&M', 'sustain', 'long-term',
                    'ongoing', 'life-cycle', 'maintain', 'monitor', 'inspect',
                    'preserve', 'manage', 'funding', 'budget', 'resources'
                ],
                'fema_priority': 'Projects must demonstrate long-term sustainability'
            }
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze plan for BRIC funding competitiveness
        Returns detailed scoring and gap analysis
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        results = {
            'overall_score': 0,
            'overall_grade': 'Unknown',
            'criteria_scores': {},
            'gaps': [],
            'strengths': [],
            'project_analysis': {},
            'recommendations': []
        }
        
        # Evaluate each BRIC criterion
        for criterion, config in self.bric_criteria.items():
            criterion_result = self._evaluate_criterion(
                text_lower, 
                config, 
                word_count
            )
            results['criteria_scores'][criterion] = criterion_result
        
        # Calculate overall BRIC score
        total_weighted_score = sum(
            score['score'] * config['weight'] 
            for score, config in zip(
                results['criteria_scores'].values(),
                self.bric_criteria.values()
            )
        )
        results['overall_score'] = round(total_weighted_score, 1)
        
        # Determine grade
        results['overall_grade'] = self._get_grade(results['overall_score'])
        
        # Analyze mitigation projects for BRIC alignment
        results['project_analysis'] = self._analyze_projects(text_lower)
        
        # Identify gaps and strengths
        results['gaps'] = self._identify_gaps(results['criteria_scores'])
        results['strengths'] = self._identify_strengths(results['criteria_scores'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(
            results['criteria_scores'],
            results['project_analysis']
        )
        
        return results
    
    def _evaluate_criterion(self, text: str, config: Dict, word_count: int) -> Dict:
        """Evaluate a single BRIC criterion"""
        
        indicator_matches = []
        for indicator in config['indicators']:
            if indicator in text:
                indicator_matches.append(indicator)
        
        # Calculate score based on unique matches and density
        unique_matches = len(set(indicator_matches))
        density = unique_matches / max(word_count / 2000, 1)  # Normalize
        
        # Determine if criterion is adequately addressed
        if unique_matches >= 5 and density > 0.5:
            status = 'Well Addressed'
            score = min(density * 100, 100)
        elif unique_matches >= 2:
            status = 'Partially Addressed'
            score = 50 + (density * 25)
        else:
            status = 'Not Addressed'
            score = max(25 * density, 10)
        
        return {
            'score': round(score, 1),
            'status': status,
            'unique_indicators': unique_matches,
            'indicators_found': list(set(indicator_matches))[:10],
            'density': round(density, 2),
            'fema_priority': config['fema_priority']
        }
    
    def _analyze_projects(self, text: str) -> Dict:
        """Analyze mitigation projects for BRIC alignment"""
        
        # Find project descriptions
        project_patterns = [
            r'project[:\s]+([^\n]{10,200})',
            r'action[:\s]+([^\n]{10,200})',
            r'mitigation[:\s]+([^\n]{10,200})',
            r'acquisition[:\s]+([^\n]{10,200})',
            r'elevation[:\s]+([^\n]{10,200})',
            r'retrofit[:\s]+([^\n]{10,200})',
            r'infrastructure[:\s]+([^\n]{10,200})'
        ]
        
        projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            projects.extend(matches[:5])  # Limit to 5 per pattern
        
        # Analyze each project for BRIC elements
        project_analysis = {
            'projects_count': len(projects),
            'projects_with_innovation': 0,
            'projects_with_climate': 0,
            'projects_with_equity': 0,
            'projects_with_maintenance': 0,
            'sample_projects': []
        }
        
        for project in projects[:10]:
            project_lower = project.lower()
            has_innovation = any(ind in project_lower for ind in self.bric_criteria['innovation']['indicators'])
            has_climate = any(ind in project_lower for ind in self.bric_criteria['climate']['indicators'])
            has_equity = any(ind in project_lower for ind in self.bric_criteria['equity']['indicators'])
            has_maintenance = any(ind in project_lower for ind in self.bric_criteria['maintenance']['indicators'])
            
            if has_innovation:
                project_analysis['projects_with_innovation'] += 1
            if has_climate:
                project_analysis['projects_with_climate'] += 1
            if has_equity:
                project_analysis['projects_with_equity'] += 1
            if has_maintenance:
                project_analysis['projects_with_maintenance'] += 1
            
            # Add to sample if has any BRIC elements
            if has_innovation or has_climate or has_equity or has_maintenance:
                project_analysis['sample_projects'].append({
                    'description': project[:100] + '...' if len(project) > 100 else project,
                    'has_innovation': has_innovation,
                    'has_climate': has_climate,
                    'has_equity': has_equity,
                    'has_maintenance': has_maintenance
                })
        
        return project_analysis
    
    def _identify_gaps(self, criteria_scores: Dict) -> List[Dict]:
        """Identify BRIC gaps"""
        
        gaps = []
        for criterion, score_data in criteria_scores.items():
            if score_data['status'] != 'Well Addressed':
                gaps.append({
                    'criterion': criterion,
                    'status': score_data['status'],
                    'description': f"{criterion.title()} components are {score_data['status'].lower()}",
                    'impact': 'May reduce BRIC competitiveness',
                    'recommendation': f"Add more {criterion}-related language and project elements"
                })
        
        return gaps
    
    def _identify_strengths(self, criteria_scores: Dict) -> List[Dict]:
        """Identify BRIC strengths"""
        
        strengths = []
        for criterion, score_data in criteria_scores.items():
            if score_data['status'] == 'Well Addressed':
                strengths.append({
                    'criterion': criterion,
                    'status': score_data['status'],
                    'description': f"{criterion.title()} is well addressed in the plan",
                    'indicators': score_data['indicators_found']
                })
        
        return strengths
    
    def _generate_recommendations(self, criteria_scores: Dict, project_analysis: Dict) -> List[Dict]:
        """Generate BRIC-specific recommendations"""
        
        recommendations = []
        
        # Check each criterion
        for criterion, score_data in criteria_scores.items():
            if score_data['score'] < 80:
                recommendations.append({
                    'priority': 'HIGH' if score_data['score'] < 50 else 'MEDIUM',
                    'criterion': criterion,
                    'action': f"Enhance {criterion} integration",
                    'details': f"Current {criterion} score is {score_data['score']}%. Add more {criterion}-focused content.",
                    'specific_suggestions': self._get_specific_suggestions(criterion)
                })
        
        # Check projects
        if project_analysis['projects_count'] > 0:
            innovation_rate = project_analysis['projects_with_innovation'] / project_analysis['projects_count']
            if innovation_rate < 0.3:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'criterion': 'project_innovation',
                    'action': 'Add innovative elements to mitigation projects',
                    'details': f"Only {int(innovation_rate*100)}% of projects include innovative elements"
                })
        
        return recommendations
    
    def _get_specific_suggestions(self, criterion: str) -> List[str]:
        """Get criterion-specific suggestions"""
        
        suggestions = {
            'innovation': [
                'Add nature-based solutions (green infrastructure, living shorelines)',
                'Include low-impact development techniques',
                'Document novel approaches to hazard mitigation',
                'Highlight pilot programs or demonstration projects'
            ],
            'climate': [
                'Add climate change projections and scenarios',
                'Include sea level rise analysis for coastal areas',
                'Document changing hazard frequencies and intensities',
                'Add compound hazard analysis',
                'Include future development climate vulnerability'
            ],
            'equity': [
                'Integrate CEJST (Climate and Economic Justice Screening Tool) data',
                'Reference Justice40 initiative',
                'Add Social Vulnerability Index (SVI) mapping',
                'Document engagement with disadvantaged communities',
                'Include environmental justice analysis'
            ],
            'maintenance': [
                'Add long-term operation and maintenance (O&M) plans',
                'Document funding mechanisms for ongoing maintenance',
                'Include lifecycle cost analysis',
                'Add monitoring and inspection schedules',
                'Document responsible parties for maintenance'
            ]
        }
        
        return suggestions.get(criterion, [])
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        
        if score >= 90:
            return 'A - Highly Competitive'
        elif score >= 80:
            return 'B - Competitive'
        elif score >= 70:
            return 'C - Moderately Competitive'
        elif score >= 60:
            return 'D - Needs Improvement'
        else:
            return 'F - Not Competitive'
