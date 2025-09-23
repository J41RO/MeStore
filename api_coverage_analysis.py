#!/usr/bin/env python3
"""
API Coverage Analysis Script
Performance Testing AI - Comprehensive endpoint coverage analysis
"""
import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class APIEndpointAnalyzer:
    def __init__(self, project_root: str = "/home/admin-jairo/MeStore"):
        self.project_root = Path(project_root)
        self.endpoints_dir = self.project_root / "app" / "api" / "v1" / "endpoints"
        self.tests_dir = self.project_root / "tests"

    def extract_endpoints_from_file(self, file_path: Path) -> List[Dict]:
        """Extract API endpoints from a Python file"""
        endpoints = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST to find route decorators
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        endpoint_info = self._extract_endpoint_info(decorator, node, content)
                        if endpoint_info:
                            endpoint_info['file'] = str(file_path.relative_to(self.project_root))
                            endpoints.append(endpoint_info)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

        return endpoints

    def _extract_endpoint_info(self, decorator, func_node, content: str) -> Dict:
        """Extract endpoint information from decorator"""
        endpoint_info = {}

        if isinstance(decorator, ast.Attribute):
            # Handle router.get, router.post, etc.
            if hasattr(decorator, 'attr') and decorator.attr in ['get', 'post', 'put', 'delete', 'patch']:
                endpoint_info['method'] = decorator.attr.upper()

        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint_info['method'] = decorator.func.attr.upper()

                    # Extract path from decorator arguments
                    if decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            endpoint_info['path'] = decorator.args[0].value
                        elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                            endpoint_info['path'] = decorator.args[0].s

        if endpoint_info and 'path' in endpoint_info:
            endpoint_info['function_name'] = func_node.name
            endpoint_info['line_number'] = func_node.lineno
            endpoint_info['complexity'] = self._estimate_complexity(func_node)
            return endpoint_info

        return None

    def _estimate_complexity(self, func_node) -> str:
        """Estimate endpoint complexity based on AST analysis"""
        complexity_score = 0

        # Count control flow statements
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                complexity_score += 1
            elif isinstance(node, ast.Call):
                complexity_score += 0.5

        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "high"

    def find_test_coverage(self, endpoints: List[Dict]) -> Dict:
        """Find existing test coverage for endpoints"""
        coverage_map = {}

        # Search for test files
        test_files = list(self.tests_dir.glob("**/test_*.py"))

        for endpoint in endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '')
            function_name = endpoint.get('function_name', '')

            coverage_map[f"{method} {path}"] = {
                'endpoint': endpoint,
                'test_files': [],
                'test_count': 0,
                'coverage_status': 'not_covered'
            }

            # Search for tests that might cover this endpoint
            for test_file in test_files:
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        test_content = f.read()

                    # Look for references to the endpoint
                    if self._endpoint_referenced_in_test(endpoint, test_content):
                        coverage_map[f"{method} {path}"]['test_files'].append(str(test_file))
                        coverage_map[f"{method} {path}"]['test_count'] += 1

                except Exception as e:
                    continue

            # Update coverage status
            if coverage_map[f"{method} {path}"]['test_count'] > 0:
                coverage_map[f"{method} {path}"]['coverage_status'] = 'covered'
            else:
                coverage_map[f"{method} {path}"]['coverage_status'] = 'not_covered'

        return coverage_map

    def _endpoint_referenced_in_test(self, endpoint: Dict, test_content: str) -> bool:
        """Check if endpoint is referenced in test content"""
        path = endpoint.get('path', '')
        method = endpoint.get('method', '').lower()
        function_name = endpoint.get('function_name', '')

        # Remove parameters from path for matching
        path_clean = re.sub(r'\{[^}]+\}', '', path)

        # Check for various patterns
        patterns = [
            f'client.{method}',
            f'"{path}"',
            f"'{path}'",
            f'test_{function_name}',
            path_clean,
            f'/{path.strip("/")}',
        ]

        for pattern in patterns:
            if pattern and pattern in test_content:
                return True

        return False

    def analyze_coverage_gaps(self) -> Dict:
        """Perform comprehensive coverage analysis"""
        print("🔍 Analyzing API endpoint coverage...")

        # Get all endpoint files
        endpoint_files = list(self.endpoints_dir.glob("*.py"))

        all_endpoints = []
        for file_path in endpoint_files:
            if file_path.name != "__init__.py":
                endpoints = self.extract_endpoints_from_file(file_path)
                all_endpoints.extend(endpoints)

        print(f"📊 Found {len(all_endpoints)} API endpoints")

        # Analyze test coverage
        coverage_map = self.find_test_coverage(all_endpoints)

        # Calculate statistics
        total_endpoints = len(coverage_map)
        covered_endpoints = sum(1 for c in coverage_map.values() if c['coverage_status'] == 'covered')
        coverage_percentage = (covered_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0

        # Categorize by priority
        high_priority = []
        medium_priority = []
        low_priority = []

        for endpoint_key, coverage_info in coverage_map.items():
            endpoint = coverage_info['endpoint']
            if coverage_info['coverage_status'] == 'not_covered':
                if endpoint.get('complexity') == 'high':
                    high_priority.append(endpoint_key)
                elif endpoint.get('complexity') == 'medium':
                    medium_priority.append(endpoint_key)
                else:
                    low_priority.append(endpoint_key)

        return {
            'total_endpoints': total_endpoints,
            'covered_endpoints': covered_endpoints,
            'coverage_percentage': coverage_percentage,
            'gap_to_85_percent': 85 - coverage_percentage,
            'coverage_map': coverage_map,
            'high_priority_gaps': high_priority,
            'medium_priority_gaps': medium_priority,
            'low_priority_gaps': low_priority,
            'endpoints_needed_for_85_percent': int((85/100 * total_endpoints) - covered_endpoints)
        }

    def generate_coverage_report(self, analysis: Dict) -> str:
        """Generate detailed coverage report"""
        report = f"""
🎯 API COVERAGE ANALYSIS REPORT
=====================================

📊 CURRENT STATUS:
- Total API Endpoints: {analysis['total_endpoints']}
- Covered Endpoints: {analysis['covered_endpoints']}
- Current Coverage: {analysis['coverage_percentage']:.1f}%
- Gap to 85% Target: {analysis['gap_to_85_percent']:.1f}%
- Endpoints Needed for 85%: {analysis['endpoints_needed_for_85_percent']}

🔥 HIGH PRIORITY GAPS ({len(analysis['high_priority_gaps'])} endpoints):
"""

        for endpoint_key in analysis['high_priority_gaps'][:10]:  # Top 10
            endpoint_info = analysis['coverage_map'][endpoint_key]['endpoint']
            report += f"  - {endpoint_key} (File: {endpoint_info['file']})\n"

        report += f"""
⚠️ MEDIUM PRIORITY GAPS ({len(analysis['medium_priority_gaps'])} endpoints):
"""

        for endpoint_key in analysis['medium_priority_gaps'][:10]:  # Top 10
            endpoint_info = analysis['coverage_map'][endpoint_key]['endpoint']
            report += f"  - {endpoint_key} (File: {endpoint_info['file']})\n"

        report += f"""
📈 COVERAGE IMPROVEMENT STRATEGY:
1. Focus on HIGH priority endpoints first (complex business logic)
2. Implement load testing scenarios that exercise critical paths
3. Add boundary and negative testing for error handling
4. Create integration tests for multi-endpoint workflows
5. Add performance testing that validates business logic

🎯 TARGET: {analysis['endpoints_needed_for_85_percent']} additional endpoint tests needed for 85% coverage
"""

        return report

def main():
    analyzer = APIEndpointAnalyzer()
    analysis = analyzer.analyze_coverage_gaps()
    report = analyzer.generate_coverage_report(analysis)

    print(report)

    # Save detailed analysis
    with open('/home/admin-jairo/MeStore/api_coverage_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print("\n💾 Detailed analysis saved to: api_coverage_analysis.json")

    return analysis

if __name__ == "__main__":
    main()