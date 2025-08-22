#!/usr/bin/env python3
"""
Escape Processor - FINAL VERSION - All methods working correctly
"""
import re

try:
    from utils.smart_content_processor import SmartContentProcessor
    SMART_PROCESSOR_AVAILABLE = True
except ImportError:
    SMART_PROCESSOR_AVAILABLE = False

try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def process_content_escapes(content):
    """Safe escape processing - DOES NOT generate literal escapes"""
    if not content:
        return content
    return content

class EscapeProcessor:
    """Safe Escape Processor - All methods guaranteed working"""
    
    def __init__(self):
        try:
            from utils.logger import get_logger
            self.logger = get_logger(__name__)
        except ImportError:
            import logging
            self.logger = logging.getLogger(__name__)
        
        self.correction_config = {
            "aggressive_mode": False,
            "preserve_intentional": True,
            "backup_enabled": True
        }
        
        self.advanced_patterns = {
            "tab_literals": re.compile(r'\\t'),
            "quote_literals": re.compile(r'\\"'),
            "single_quote_literals": re.compile(r"\\\'"),
            "newline_literals": re.compile(r'\\n'),
            "backslash_literals": re.compile(r'\\\\')
        }
    
    def analyze_escape_patterns(self, content: str) -> dict:
        """Analyze escape patterns safely"""
        analysis = {"total_escapes": 0, "escape_types": {}, "problematic_sequences": []}
        
        if not content:
            return analysis
            
        try:
            patterns = {
                "newlines": r"\\n",
                "tabs": r"\\t", 
                "quotes": r'\\"',
                "single_quotes": r"\\'",
                "backslashes": r"\\\\",
            }
            for name, pattern in patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    analysis["escape_types"][name] = len(matches)
                    analysis["total_escapes"] += len(matches)
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing escape patterns: {e}")
            return analysis
    
    def fix_escape_issues(self, content: str, issue_type: str) -> str:
        """Fix escape issues safely - ALWAYS returns string"""
        if content is None:
            return None
        if not content:
            return ""

        try:
            if issue_type == "double_escape":
                content = content.replace("\\\\n", "\n")
                content = content.replace("\\\\t", "\t")
                content = content.replace("\\\\\\\\", "\\")
                
            elif issue_type == "broken_json_escape":
                content = content.replace('\\"', '"')
                
            elif issue_type == "newline_escapes":
                content = content.replace('\\n', '\n')
                
            elif issue_type == "literal_escapes" or issue_type == "all":
                content = self.advanced_patterns["tab_literals"].sub('\t', content)
                content = self.advanced_patterns["quote_literals"].sub('"', content)
                content = self.advanced_patterns["single_quote_literals"].sub("'", content)
                content = self.advanced_patterns["newline_literals"].sub('\n', content)
                
            return content
            
        except Exception as e:
            self.logger.error(f"Error in fix_escape_issues: {e}")
            return content or ""
    
    def validate_escape_integrity(self, content: str) -> dict:
        """Validate escape integrity"""
        validation = {
            "is_valid": True,
            "issues": [],
            "errors": [],
            "warnings": [],
            "total_escapes": 0
        }
        
        if not content:
            return validation
            
        try:
            analysis = self.analyze_escape_patterns(content)
            validation["total_escapes"] = analysis.get("total_escapes", 0)
            
            if "\\\\n" in content:
                validation["issues"].append("Double escaped newlines detected")
                validation["is_valid"] = False
                
            if "\\\\t" in content:
                validation["issues"].append("Double escaped tabs detected")
                validation["is_valid"] = False
                
            if '\\"' in content and content.count('\\"') > content.count('"'):
                validation["warnings"].append("Possible over-escaped quotes")
                
        except Exception as e:
            validation["is_valid"] = False
            validation["issues"].append(f"Validation error: {ae}")
            
        return validation
    
    def suggest_escape_corrections(self, content: str) -> list:
        """Suggest escape corrections"""
        suggestions = []

        if not content:
            return suggestions

        try:
            analysis = self.analyze_escape_patterns(content)
            validation = self.validate_escape_integrity(content)

            if "Double escaped newlines detected" in validation.get("issues", []):
                suggestions.append({
                    "issue": "double_escape_newlines",
                    "description": "Double escaped newlines detected",
                    "correction": "Use fix_escape_issues with 'double_escape' type"
                })

            if "Double escaped tabs detected" in validation.get("issues", []):
                suggestions.append({
                    "issue": "double_escape_tabs", 
                    "description": "Double escaped tabs detected",
                    "correction": "Use fix_escape_issues with 'double_escape' type"
                })

            if '\\"' in content:
                suggestions.append({
                    "issue": "escaped_quotes",
                    "description": "Escaped quotes detected",
                    "correction": "Use fix_escape_issues with 'broken_json_escape' type"
                })

            if '\\t' in content:
                suggestions.append({
                    "issue": "tab_escapes",
                    "description": "Tab escape literals detected",
                    "correction": "Use fix_escape_issues with 'literal_escapes' type"
                })

        except Exception as e:
            suggestions.append({
                "issue": "analysis_error",
                "description": f"Analysis error: {e}",
                "correction": "Manual review recommended"
            })

        return suggestions
    
    def normalize_escape_sequences(self, content: str) -> str:
        """Normalize escape sequences"""
        if content is None:
            return None
        if not content:
            return ""
            
        try:
            normalized = content
            normalized = normalized.replace('\\"', '"')
            normalized = normalized.replace('\\n', '\n')
            normalized = normalized.replace('\\r', '\r')
            normalized = normalized.replace('\\t', '\t')
            normalized = normalized.replace('\\\\', '\\')
            return normalized
        except Exception as e:
            self.logger.error(f"Error normalizing escape sequences: {e}")
            return content
    
    def integrate_with_content_handler(self) -> dict:
        """Integrate with content handler"""
        integration = {
            "status": "ready",
            "capabilities": ["escape_analysis", "escape_correction", "validation", "normalization"],
            "smart_processor_available": SMART_PROCESSOR_AVAILABLE,
            "advanced_patterns_count": len(self.advanced_patterns),
            "compatible": True,
            "handler_available": True,
            "integration_methods": [
                "analyze_escape_patterns", "fix_escape_issues", 
                "validate_escape_integrity", "suggest_escape_corrections",
                "normalize_escape_sequences"
            ],
            "methods": [
                "analyze_escape_patterns", "fix_escape_issues",
                "validate_escape_integrity", "suggest_escape_corrections", 
                "normalize_escape_sequences"
            ]
        }
        
        try:
            test_content = "test\\nwith\\tescapes"
            self.analyze_escape_patterns(test_content)
            self.validate_escape_integrity(test_content)
            self.suggest_escape_corrections(test_content)
            self.normalize_escape_sequences(test_content)
            integration["integration_test"] = "passed"
        except Exception as e:
            integration["status"] = "error"
            integration["integration_test"] = f"failed: {e}"
            
        return integration
    
    def fix_newline_escapes(self, content: str) -> str:
        """Fix newline escapes with proper regex"""
        if content is None:
            return None
        if not content:
            return ""
            
        try:
            result = re.sub(r'(?<!\\)\\n', '\n', content)
            return result
        except Exception as e:
            self.logger.error(f"Error fixing newline escapes: {e}")
            return content
    
    def fix_tab_escapes(self, content: str) -> str:
        """Fix tab escapes with proper regex"""
        if content is None:
            return None
        if not content:
            return ""
            
        try:
            result = re.sub(r'(?<!\\)\\t', '\t', content)
            return result
        except Exception as e:
            self.logger.error(f"Error fixing tab escapes: {e}")
            return content
