#!/usr/bin/env python3
"""
Enhanced API Coverage Analysis Script
Performance Testing AI - Comprehensive endpoint coverage analysis using regex patterns
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import subprocess

class EnhancedAPIAnalyzer:
    def __init__(self, project_root: str = "/home/admin-jairo/MeStore"):
        self.project_root = Path(project_root)
        self.endpoints_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        self.tests_dir = self.project_root / "tests"

    def extract_endpoints_using_regex(self) -> List[Dict]:
        """Extract API endpoints using regex patterns"""
        endpoints = []

        # Get all endpoint files
        endpoint_files = list(self.endpoints_dir.glob("*.py"))

        for file_path in endpoint_files:
            if file_path.name == "__init__.py":
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Regex pattern to find router decorators
                pattern = r'@router\.(get|post|put|delete|patch)\(\s*[\'"](.*?)[\'"]\s*.*?\)\s*\n\s*async def (\w+)'

                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    function_name = match.group(3)

                    # Estimate complexity by counting lines in function
                    func_start = match.end()
                    func_content = self._extract_function_content(content, func_start)
                    complexity = self._estimate_complexity_by_content(func_content)

                    endpoint = {
                        'method': method,
                        'path': path,
                        'function_name': function_name,
                        'file': str(file_path.relative_to(self.project_root)),
                        'complexity': complexity,
                        'file_name': file_path.name
                    }

                    endpoints.append(endpoint)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        return endpoints

    def _extract_function_content(self, content: str, start_pos: int) -> str:
        """Extract function content starting from a position"""
        lines = content[start_pos:].split('\n')
        func_lines = []
        indent_level = None

        for line in lines[:50]:  # Limit to first 50 lines
            if line.strip() == "":
                continue

            current_indent = len(line) - len(line.lstrip())

            if indent_level is None:
                indent_level = current_indent
            elif current_indent <= indent_level and line.strip():
                # Function ended
                break

            func_lines.append(line)

        return '\n'.join(func_lines)

    def _estimate_complexity_by_content(self, content: str) -> str:
        """Estimate complexity by analyzing function content"""
        complexity_indicators = [
            'if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except',
            'await ', 'async ', '.query(', '.filter(', '.join(', 'transaction'
        ]

        score = 0
        for indicator in complexity_indicators:
            score += content.count(indicator)

        if score <= 3:
            return "low"
        elif score <= 8:
            return "medium"
        else:
            return "high"

    def find_test_coverage_enhanced(self, endpoints: List[Dict]) -> Dict:
        """Enhanced test coverage analysis"""
        coverage_map = {}

        # Find all test files
        test_files = list(self.tests_dir.glob("**/test_*.py"))

        print(f"🔍 Analyzing {len(test_files)} test files for {len(endpoints)} endpoints...")

        for endpoint in endpoints:
            endpoint_key = f"{endpoint['method']} {endpoint['path']}"
            coverage_map[endpoint_key] = {
                'endpoint': endpoint,
                'test_files': [],
                'test_functions': [],
                'test_count': 0,
                'coverage_status': 'not_covered',
                'coverage_confidence': 0
            }

            # Search for test coverage
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        test_content = f.read()

                    confidence, test_functions = self._analyze_endpoint_coverage(endpoint, test_content)

                    if confidence > 0:
                        coverage_map[endpoint_key]['test_files'].append(str(test_file.relative_to(self.project_root)))
                        coverage_map[endpoint_key]['test_functions'].extend(test_functions)
                        coverage_map[endpoint_key]['test_count'] += len(test_functions)
                        coverage_map[endpoint_key]['coverage_confidence'] = max(
                            coverage_map[endpoint_key]['coverage_confidence'], confidence
                        )

                except Exception as e:
                    continue

            # Update coverage status based on confidence
            if coverage_map[endpoint_key]['coverage_confidence'] >= 70:
                coverage_map[endpoint_key]['coverage_status'] = 'well_covered'
            elif coverage_map[endpoint_key]['coverage_confidence'] >= 30:
                coverage_map[endpoint_key]['coverage_status'] = 'partially_covered'
            else:
                coverage_map[endpoint_key]['coverage_status'] = 'not_covered'

        return coverage_map

    def _analyze_endpoint_coverage(self, endpoint: Dict, test_content: str) -> Tuple[int, List[str]]:
        """Analyze how well an endpoint is covered in test content"""
        confidence = 0
        test_functions = []

        method = endpoint['method'].lower()
        path = endpoint['path']
        function_name = endpoint['function_name']
        file_name = endpoint['file_name'].replace('.py', '')

        # Find test functions that might test this endpoint
        test_func_pattern = r'(def test_\w+|async def test_\w+)'
        test_funcs = re.findall(test_func_pattern, test_content)

        # Scoring patterns
        patterns = [
            (f'client.{method}', 25),  # HTTP method call
            (f'"{path}"', 20),         # Exact path match
            (f"'{path}'", 20),         # Exact path match
            (f'test_{function_name}', 30),  # Function name test
            (f'{file_name}', 10),      # File name reference
            (f'/{path.strip("/")}', 15),  # Path without quotes
        ]

        # Check for patterns and calculate confidence
        for pattern, points in patterns:
            if pattern and pattern in test_content:
                confidence += points

                # Find which test functions contain this pattern
                lines = test_content.split('\n')
                current_func = None

                for line in lines:
                    func_match = re.search(r'def (test_\w+)', line)
                    if func_match:
                        current_func = func_match.group(1)
                    elif pattern in line and current_func:
                        if current_func not in test_functions:
                            test_functions.append(current_func)

        # Cap confidence at 100
        confidence = min(confidence, 100)

        return confidence, test_functions

    def analyze_critical_gaps(self) -> Dict:
        """Comprehensive analysis focusing on coverage gaps"""
        print("🚀 Starting Enhanced API Coverage Analysis...")

        endpoints = self.extract_endpoints_using_regex()
        print(f"📊 Discovered {len(endpoints)} API endpoints")

        coverage_map = self.find_test_coverage_enhanced(endpoints)

        # Calculate statistics
        total_endpoints = len(coverage_map)
        well_covered = sum(1 for c in coverage_map.values() if c['coverage_status'] == 'well_covered')
        partially_covered = sum(1 for c in coverage_map.values() if c['coverage_status'] == 'partially_covered')
        not_covered = sum(1 for c in coverage_map.values() if c['coverage_status'] == 'not_covered')

        current_coverage = ((well_covered + partially_covered * 0.5) / total_endpoints * 100) if total_endpoints > 0 else 0

        # Categorize gaps by priority
        critical_gaps = []
        high_priority_gaps = []
        medium_priority_gaps = []
        low_priority_gaps = []

        for endpoint_key, info in coverage_map.items():
            endpoint = info['endpoint']
            if info['coverage_status'] in ['not_covered', 'partially_covered']:

                # Business criticality scoring
                criticality_score = self._calculate_business_criticality(endpoint)

                gap_info = {
                    'endpoint_key': endpoint_key,
                    'endpoint': endpoint,
                    'coverage_info': info,
                    'criticality_score': criticality_score
                }

                if criticality_score >= 90:
                    critical_gaps.append(gap_info)
                elif criticality_score >= 70:
                    high_priority_gaps.append(gap_info)
                elif criticality_score >= 40:
                    medium_priority_gaps.append(gap_info)
                else:
                    low_priority_gaps.append(gap_info)

        # Sort by criticality
        critical_gaps.sort(key=lambda x: x['criticality_score'], reverse=True)
        high_priority_gaps.sort(key=lambda x: x['criticality_score'], reverse=True)
        medium_priority_gaps.sort(key=lambda x: x['criticality_score'], reverse=True)

        endpoints_needed_for_85 = max(0, int((85/100 * total_endpoints) - well_covered - partially_covered))

        return {
            'total_endpoints': total_endpoints,
            'well_covered': well_covered,
            'partially_covered': partially_covered,
            'not_covered': not_covered,
            'current_coverage_percentage': current_coverage,
            'gap_to_85_percent': 85 - current_coverage,
            'endpoints_needed_for_85_percent': endpoints_needed_for_85,
            'coverage_map': coverage_map,
            'critical_gaps': critical_gaps,
            'high_priority_gaps': high_priority_gaps,
            'medium_priority_gaps': medium_priority_gaps,
            'low_priority_gaps': low_priority_gaps,
        }

    def _calculate_business_criticality(self, endpoint: Dict) -> int:
        """Calculate business criticality score for an endpoint"""
        score = 50  # Base score

        method = endpoint['method']
        path = endpoint['path']
        function_name = endpoint['function_name']
        file_name = endpoint['file_name']
        complexity = endpoint['complexity']

        # Business critical keywords
        critical_keywords = {
            'auth': 25, 'login': 25, 'register': 20, 'token': 15,
            'payment': 30, 'pay': 25, 'transaction': 25, 'order': 20,
            'admin': 20, 'user': 15, 'vendor': 15, 'product': 15,
            'commission': 20, 'webhook': 25, 'security': 20,
            'dashboard': 15, 'analytics': 10, 'health': 5
        }

        # Check for critical keywords
        text_to_check = f"{path} {function_name} {file_name}".lower()
        for keyword, points in critical_keywords.items():
            if keyword in text_to_check:
                score += points

        # HTTP method scoring
        method_scores = {
            'POST': 15,  # Create operations are critical
            'PUT': 10,   # Update operations
            'DELETE': 20, # Delete operations are very critical
            'GET': 5,    # Read operations less critical
            'PATCH': 8   # Partial updates
        }
        score += method_scores.get(method, 0)

        # Complexity scoring
        complexity_scores = {'high': 15, 'medium': 10, 'low': 5}
        score += complexity_scores.get(complexity, 0)

        # Path depth scoring (deeper paths often more specific/critical)
        path_depth = path.count('/')
        score += min(path_depth * 3, 15)

        return min(score, 100)

    def generate_performance_testing_report(self, analysis: Dict) -> str:
        """Generate comprehensive performance testing focused report"""
        report = f"""
🎯 PERFORMANCE TESTING AI - API COVERAGE ACCELERATION REPORT
================================================================

📊 CURRENT COVERAGE STATUS:
- Total API Endpoints: {analysis['total_endpoints']}
- Well Covered: {analysis['well_covered']} ({analysis['well_covered']/analysis['total_endpoints']*100:.1f}%)
- Partially Covered: {analysis['partially_covered']} ({analysis['partially_covered']/analysis['total_endpoints']*100:.1f}%)
- Not Covered: {analysis['not_covered']} ({analysis['not_covered']/analysis['total_endpoints']*100:.1f}%)
- Current Coverage: {analysis['current_coverage_percentage']:.1f}%
- Gap to 85% Target: {analysis['gap_to_85_percent']:.1f}%

🚨 CRITICAL COVERAGE GAPS ({len(analysis['critical_gaps'])} endpoints):
===============================================================
"""

        for i, gap in enumerate(analysis['critical_gaps'][:5]):  # Top 5 critical
            endpoint = gap['endpoint']
            report += f"""
{i+1}. {gap['endpoint_key']} (Score: {gap['criticality_score']})
   File: {endpoint['file']}
   Function: {endpoint['function_name']}
   Complexity: {endpoint['complexity']}
   Coverage Status: {gap['coverage_info']['coverage_status']}
   Confidence: {gap['coverage_info']['coverage_confidence']}%
"""

        report += f"""
🔥 HIGH PRIORITY GAPS ({len(analysis['high_priority_gaps'])} endpoints):
===========================================================
"""

        for i, gap in enumerate(analysis['high_priority_gaps'][:8]):  # Top 8 high priority
            endpoint = gap['endpoint']
            report += f"""
{i+1}. {gap['endpoint_key']} (Score: {gap['criticality_score']})
   File: {endpoint['file']}
   Complexity: {endpoint['complexity']}
"""

        report += f"""
📈 PERFORMANCE TESTING STRATEGY FOR 85% COVERAGE:
=================================================

🎯 IMMEDIATE ACTIONS (Target: {analysis['endpoints_needed_for_85_percent']} endpoints):
1. Focus on CRITICAL gaps first ({len(analysis['critical_gaps'])} endpoints)
2. Implement comprehensive load testing for auth/payment endpoints
3. Create boundary testing for all POST/PUT/DELETE operations
4. Add negative testing for error handling paths

⚡ HIGH-IMPACT TEST SCENARIOS:
1. Authentication flow load testing (login, register, token refresh)
2. Payment processing stress testing (multiple concurrent transactions)
3. Admin operations capacity testing (bulk operations)
4. Vendor dashboard performance validation
5. Product catalog stress testing with search/filtering

🔧 LOAD TESTING SCENARIOS THAT INCREASE COVERAGE:
1. Multi-user concurrent vendor registration
2. Bulk product operations under load
3. Commission calculation stress testing
4. Real-time analytics performance validation
5. File upload capacity testing

📊 PERFORMANCE BENCHMARKS FOR NEW TESTS:
- Response Time: <200ms for GET, <500ms for POST/PUT
- Throughput: >100 RPS for critical endpoints
- Error Rate: <1% under normal load
- Concurrent Users: 100+ for critical business flows

🚀 IMPLEMENTATION PRIORITY:
1. Week 1: Critical gaps (auth, payments, admin core)
2. Week 2: High priority gaps (vendor operations, products)
3. Week 3: Load testing scenarios for covered endpoints
4. Week 4: Integration and boundary testing

⏱️ ESTIMATED IMPACT:
- Coverage improvement: +{analysis['gap_to_85_percent']:.1f}% to reach 85% target
- Performance validation: 100% of critical business paths
- Load testing coverage: 90% of high-traffic endpoints
- Business continuity: Validated under 500+ concurrent users
"""

        return report

def main():
    analyzer = EnhancedAPIAnalyzer()
    analysis = analyzer.analyze_critical_gaps()
    report = analyzer.generate_performance_testing_report(analysis)

    print(report)

    # Save detailed analysis
    with open('/home/admin-jairo/MeStore/enhanced_api_coverage_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print("\n💾 Detailed analysis saved to: enhanced_api_coverage_analysis.json")

    return analysis

if __name__ == "__main__":
    main()