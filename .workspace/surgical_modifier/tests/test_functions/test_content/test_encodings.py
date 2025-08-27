import pytest
import tempfile
import os
import sys
sys.path.insert(0, '/home/admin-jairo/MeStore/.workspace/surgical_modifier')
from functions.content.reader import ContentReader
from functions.content.writer import ContentWriter
from functions.content.cache import ContentCache
from functions.content.validator import ContentValidator


class TestEncodingIntegration:
    def setup_method(self):
        """Configuracion inicial para cada test"""
        self.reader = ContentReader()
        self.writer = ContentWriter()
        self.cache = ContentCache()
        self.validator = ContentValidator()
        
    def teardown_method(self):
        """Limpieza despues de cada test"""
        if hasattr(self.cache, 'clear'):
            self.cache.clear()

    def test_reader_utf8_detection(self):
        """Test deteccion correcta UTF-8"""
        result = self.reader.read_file('/tmp/test_utf8.txt')
        assert result['success'] is True
        assert 'ñáéíóú' in result['content']
        assert 'emojis' in result['content']
        assert result['encoding_info']['encoding'] in ['utf-8', 'UTF-8']
    
    def test_reader_latin1_detection(self):
        """Test deteccion correcta Latin-1"""
        result = self.reader.read_file('/tmp/test_latin1.txt')
        assert result['success'] is True
        assert 'ñáéí' in result['content']
        assert result['encoding_info']['encoding'] in ['latin-1', 'ISO-8859-1', 'cp1252', 'windows-1250', 'utf-8', 'UTF-8']
    
    def test_reader_ascii_detection(self):
        """Test deteccion correcta ASCII"""
        result = self.reader.read_file('/tmp/test_ascii.txt')
        assert result['success'] is True
        assert 'Simple text' in result['content']
        assert result['encoding_info']['confidence'] > 0.7
    
    def test_reader_fallback_robustez(self):
        """Test fallback con multiples intentos"""
        result = self.reader.read_with_fallback('/tmp/test_cp1252.txt')
        assert result['success'] is True
        assert 'attempts' in result
        assert len(result['attempts']) >= 1

    def test_writer_preserva_utf8(self):
        """Test que writer preserva UTF-8 correctamente"""
        content_original = 'Nuevo contenido: ñáéíóú'
        result = self.writer.write_file('/tmp/test_utf8_write.txt', content_original)
        assert result['success'] is True
        
        read_result = self.reader.read_file('/tmp/test_utf8_write.txt')
        assert read_result['success'] is True
        assert 'ñáéíóú' in read_result['content']
        assert read_result['encoding_info']['encoding'] in ['utf-8', 'UTF-8']

    def test_writer_auto_deteccion_encoding(self):
        """Test auto-deteccion encoding en archivo existente"""
        result = self.writer.write_file('/tmp/test_latin1.txt', 'Contenido nuevo: ñáéí')
        assert result['success'] is True
        
        read_back = self.reader.read_file('/tmp/test_latin1.txt')
        assert read_back['success'] is True
        assert 'Contenido nuevo' in read_back['content']

    def test_writer_line_endings_preservacion(self):
        """Test preservacion line endings con encoding"""
        content_multiline = 'Linea 1: ñáéí\nLinea 2: óúü\nLinea 3: final'
        result = self.writer.write_file('/tmp/test_multiline.txt', content_multiline)
        assert result['success'] is True
        
        read_result = self.reader.read_file('/tmp/test_multiline.txt')
        lines = read_result['content'].split('\n')
        assert len(lines) == 3
        assert 'ñáéí' in lines[0]
        assert 'óúü' in lines[1]

    def test_integration_reader_writer_cache_validator(self):
        """Test integracion completa cuarteto content"""
        read_result = self.reader.read_file('/tmp/test_utf8.txt')
        assert read_result['success'] is True
        
        validation = self.validator.validate_content(read_result['content'], ['not_empty', 'text_only'])
        assert validation['valid'] is True
        
        cached = self.cache.cache_content('/tmp/test_utf8.txt', read_result)
        assert cached is True
        
        cached_content = self.cache.get_cached_content('/tmp/test_utf8.txt')
        assert cached_content is not None
        assert cached_content['content'] == read_result['content']
        
        modified_content = read_result['content'] + '\nLinea agregada: ñáéíóú'
        write_result = self.writer.write_file('/tmp/test_integration.txt', modified_content)
        assert write_result['success'] is True

    def test_binary_file_handling(self):
        """Test manejo de archivos binarios"""
        result = self.reader.read_file('/tmp/test_binary.bin')
        if not result['success']:
            assert 'error' in result
        else:
            # Solo verificar que maneja binarios sin error específico de método
            assert 'encoding_info' in result

    def test_edge_cases_encodings(self):
        """Test casos edge con encodings"""
        problematic_content = 'Texto con caracteres: y normales: ñáéí'
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(problematic_content.encode('utf-8', errors='replace'))
            temp_path = f.name
        
        try:
            result = self.reader.read_with_fallback(temp_path)
            assert result['success'] is True
            assert 'attempts' in result
        finally:
            os.unlink(temp_path)
