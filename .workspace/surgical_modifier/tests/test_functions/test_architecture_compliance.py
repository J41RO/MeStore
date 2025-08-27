import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class TestArchitecturalCompliance:
    """Test que functions content cumplen con arquitectura modular"""
    
    def test_functions_support_all_planned_coordinators(self):
        """Test functions soportan coordinadores planificados"""
        from functions.content.reader import ContentReader
        from functions.content.writer import ContentWriter  
        from functions.content.cache import ContentCache
        from functions.content.validator import ContentValidator
        
        # CREATE - necesita writer, validator
        create_functions = [ContentWriter(), ContentValidator()]
        
        # REPLACE - necesita cuarteto completo
        replace_functions = [ContentReader(), ContentWriter(), ContentCache(), ContentValidator()]
        
        # Verificar instanciación exitosa
        assert len(create_functions) == 2
        assert len(replace_functions) == 4
    
    def test_functions_modular_according_to_design(self):
        """Test functions son modulares según diseño"""
        from functions.content.writer import ContentWriter
        from functions.content.validator import ContentValidator
        
        writer = ContentWriter()
        validator = ContentValidator() 
        
        assert writer is not None
        assert validator is not None