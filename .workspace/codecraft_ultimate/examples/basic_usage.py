#!/usr/bin/env python3
"""
🚀 CodeCraft Ultimate v6.0 - Basic Usage Examples
Demonstrates core functionality and AI collaboration patterns
"""

import subprocess
import json
import os

def run_codecraft_command(command):
    """Execute CodeCraft command and return structured result"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Try to parse as JSON for structured output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {'output': result.stdout, 'success': True}
    
    except subprocess.CalledProcessError as e:
        return {'error': e.stderr, 'success': False}

def example_surgical_operations():
    """Example: Enhanced surgical operations from v5.3"""
    
    print("🔧 SURGICAL OPERATIONS EXAMPLES")
    print("=" * 50)
    
    # Create a sample file
    result = run_codecraft_command(
        'codecraft create example.py "def hello():\n    print(\'Hello World\')"'
    )
    print("✅ Created file:", result)
    
    # Replace content
    result = run_codecraft_command(
        'codecraft replace example.py "Hello World" "Hello CodeCraft"'
    )
    print("✅ Replaced content:", result)

def example_analysis_operations():
    """Example: Deep code analysis"""
    
    print("\n🔍 ANALYSIS OPERATIONS EXAMPLES")
    print("=" * 50)
    
    # Analyze complexity
    result = run_codecraft_command(
        'codecraft analyze-complexity . --format=json --output-format=json'
    )
    print("✅ Complexity analysis:", result)

def example_ai_collaboration():
    """Example: AI collaboration workflow"""
    
    print("\n🤝 AI COLLABORATION WORKFLOW EXAMPLE")
    print("=" * 50)
    
    # Step 1: AI requests project analysis
    print("🤖 AI: Analyzing project structure...")
    result = run_codecraft_command(
        'codecraft project-health . --output-format=json'
    )
    
    if result.get('success'):
        # Step 2: AI interprets results
        health_score = result.get('data', {}).get('health_score', 0)
        print(f"🤖 AI: Project health score is {health_score}")

if __name__ == "__main__":
    print("🚀 CodeCraft Ultimate v6.0 - Examples")
    print("=====================================")
    
    example_surgical_operations()
    example_analysis_operations() 
    example_ai_collaboration()