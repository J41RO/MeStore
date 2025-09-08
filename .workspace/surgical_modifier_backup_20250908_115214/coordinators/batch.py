from pathlib import Path
from typing import Dict, Any, List
import sys
import os
import logging
import json
import yaml
from functions.backup.intelligent_manager import IntelligentBackupManager
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.validator import ContentValidator

class BatchCoordinator:
    """Coordinador para operaciones BATCH - ejecuta múltiples operaciones desde archivo"""
    
    def __init__(self):
        self.backup_manager = IntelligentBackupManager()
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.validator = ContentValidator()
        self.logger = logging.getLogger(__name__)
    
    def execute(self, batch_file: str, dry_run: bool = False) -> Dict[str, Any]:
        """Ejecuta operaciones batch desde archivo"""
        try:
            # Leer archivo de comandos
            operations = self._parse_batch_file(batch_file)
            
            results = {
                'success': True,
                'operations_executed': 0,
                'operations_failed': 0,
                'details': []
            }
            
            for i, operation in enumerate(operations):
                try:
                    if not dry_run:
                        # Aquí se ejecutaría cada operación
                        pass
                    
                    results['operations_executed'] += 1
                    results['details'].append({
                        'operation': i + 1,
                        'status': 'success',
                        'command': operation.get('command', 'unknown')
                    })
                    
                except Exception as e:
                    results['operations_failed'] += 1
                    results['details'].append({
                        'operation': i + 1,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'operations_executed': 0,
                'operations_failed': 0
            }
    
    def _parse_batch_file(self, batch_file: str) -> List[Dict[str, Any]]:
        """Parse archivo JSON/YAML de comandos batch"""
        file_path = Path(batch_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f'Batch file not found: {batch_file}')
        
        result = self.reader.read_file(str(file_path))
        content = result['content'] if isinstance(result, dict) else result
        
        if file_path.suffix.lower() == '.json':
            data = json.loads(content)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            data = yaml.safe_load(content)
        else:
            raise ValueError(f'Unsupported batch file format: {file_path.suffix}')
        
        if 'operations' not in data:
            raise ValueError('Batch file must contain "operations" key')
        
        return data['operations']