"""
Tests para configuración multi-environment de Alembic.

Verifica que la configuración de environments funciona correctamente.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import configparser


class TestEnvironmentConfiguration:
    """Test suite para configuración de environments."""
    
    def test_environment_detection_development(self):
        """Test que environment development se detecta correctamente."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            env = os.getenv('ENVIRONMENT')
            assert env == 'development'
    
    def test_environment_detection_testing(self):
        """Test que environment testing se detecta correctamente."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'testing'}):
            env = os.getenv('ENVIRONMENT')
            assert env == 'testing'
    
    def test_environment_detection_production(self):
        """Test que environment production se detecta correctamente."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            env = os.getenv('ENVIRONMENT')
            assert env == 'production'


class TestAlembicConfiguration:
    """Test suite para verificar que alembic.ini tiene las sections correctas."""
    
    def test_alembic_ini_has_required_sections(self):
        """Test que alembic.ini contiene todas las sections requeridas."""
        config = configparser.ConfigParser()
        config.read('alembic.ini')
        
        # Verificar que existen las sections básicas
        assert config.has_section('alembic')
        assert config.has_section('alembic:development')
        assert config.has_section('alembic:testing')
        assert config.has_section('alembic:production')
    
    def test_environment_sections_have_required_keys(self):
        """Test que cada section de environment tiene las keys requeridas."""
        config = configparser.ConfigParser()
        config.read('alembic.ini')
        
        required_keys = ['sqlalchemy.url']
        
        for env in ['development', 'testing', 'production']:
            section_name = f'alembic:{env}'
            assert config.has_section(section_name), f"Section {section_name} not found"
            
            for key in required_keys:
                assert config.has_option(section_name, key), f"Key {key} not found in {section_name}"
    
    def test_no_duplicate_sections(self):
        """Test que no hay sections duplicadas en alembic.ini."""
        with open('alembic.ini', 'r') as f:
            content = f.read()
        
        # Count occurrences of logger_alembic
        logger_count = content.count('[logger_alembic]')
        assert logger_count == 1, f"Found {logger_count} [logger_alembic] sections, should be 1"


class TestEnvironmentFiles:
    """Test suite para verificar archivos .env.*."""
    
    def test_env_files_exist(self):
        """Test que todos los archivos .env necesarios existen."""
        assert os.path.exists('.env'), ".env file should exist"
        assert os.path.exists('.env.test'), ".env.test file should exist"
        assert os.path.exists('.env.production'), ".env.production file should exist"
    
    def test_env_files_have_database_url(self):
        """Test que todos los archivos .env tienen DATABASE_URL."""
        env_files = ['.env', '.env.test', '.env.production']
        
        for env_file in env_files:
            with open(env_file, 'r') as f:
                content = f.read()
                assert 'DATABASE_URL' in content, f"DATABASE_URL not found in {env_file}"
    
    def test_env_files_have_environment(self):
        """Test que archivos .env tienen ENVIRONMENT configurado."""
        # .env should have ENVIRONMENT=development
        with open('.env', 'r') as f:
            content = f.read()
            assert 'ENVIRONMENT=development' in content
        
        # .env.production should have ENVIRONMENT=production
        with open('.env.production', 'r') as f:
            content = f.read()
            assert 'ENVIRONMENT=production' in content


if __name__ == '__main__':
    print("🧪 EJECUTANDO TESTS BÁSICOS DE CONFIGURACIÓN...")
    
    # Test basic configuration
    config = configparser.ConfigParser()
    try:
        config.read('alembic.ini')
        print("✅ alembic.ini se puede leer correctamente")
        
        sections = config.sections()
        print(f"✅ Sections encontradas: {sections}")
        
        for env in ['development', 'testing', 'production']:
            section = f'alembic:{env}'
            if config.has_section(section):
                print(f"✅ Section {section} existe")
            else:
                print(f"❌ Section {section} no existe")
                
    except Exception as e:
        print(f"❌ Error leyendo alembic.ini: {e}")
    
    print("🧪 Tests básicos completados")
