from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class StructuralIssue:
    """Representa un problema estructural detectado"""
    type: str  # 'duplicate_interface', 'circular_import', 'broken_syntax', etc.
    severity: str  # 'error', 'warning', 'info'
    file_path: str
    line_number: Optional[int]
    message: str
    details: Dict[str, Any]

@dataclass
class AnalysisResult:
    """Resultado del análisis estructural"""
    has_issues: bool
    issues: List[StructuralIssue]
    analysis_time: float
    files_analyzed: int
    
    def get_critical_issues(self) -> List[StructuralIssue]:
        """Retorna solo los problemas críticos"""
        return [issue for issue in self.issues if issue.severity == 'error']
    
    def get_warnings(self) -> List[StructuralIssue]:
        """Retorna solo las advertencias"""
        return [issue for issue in self.issues if issue.severity == 'warning']
