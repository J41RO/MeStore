"""
Tests para configuración unificada de DATABASE_URL.

Verifica que la configuración de base de datos funcione correctamente
desde variables de entorno usando Pydantic Settings.
"""

import os
import pytest
from unittest.mock import patch

from app.core.config import Settings


class TestDatabaseConfiguration:
   """Tests para configuración DATABASE_URL unificada."""

   def test_default_database_url(self):
       """Test que verifica DATABASE_URL por defecto."""
       settings = Settings()

       assert settings.DATABASE_URL.startswith('postgresql+asyncpg://')
       assert 'mestocker_user' in settings.DATABASE_URL
       assert 'mestocker_dev' in settings.DATABASE_URL
       assert settings.DB_ECHO is False

   @patch.dict(os.environ, {'DATABASE_URL': 'postgresql+asyncpg://test:test@test:5432/test'})
   def test_database_url_from_env(self):
       """Test que verifica carga desde variable de entorno."""
       settings = Settings()

       assert settings.DATABASE_URL == 'postgresql+asyncpg://test:test@test:5432/test'

   @patch.dict(os.environ, {'DB_ECHO': 'true'})
   def test_db_echo_from_env(self):
       """Test que verifica DB_ECHO desde entorno."""
       settings = Settings()

       assert settings.DB_ECHO is True

   def test_database_url_validation_success(self):
       """Test que verifica validación exitosa de DATABASE_URL."""
       settings = Settings()

       # Validar que acepta postgresql://
       settings.DATABASE_URL = 'postgresql://user:pass@host:5432/db'
       assert settings.DATABASE_URL.startswith('postgresql://')

       # Validar que acepta postgresql+asyncpg://
       settings.DATABASE_URL = 'postgresql+asyncpg://user:pass@host:5432/db'
       assert settings.DATABASE_URL.startswith('postgresql+asyncpg://')

   def test_database_url_validation_failure(self):
       """Test que verifica fallo de validación para URLs inválidas."""
       with pytest.raises(ValueError, match='DATABASE_URL must use postgresql'):
           Settings(DATABASE_URL='mysql://user:pass@host:5432/db')

   def test_additional_db_fields(self):
       """Test que verifica campos adicionales de configuración DB."""
       settings = Settings()

       assert settings.DB_HOST == 'localhost'
       assert settings.DB_PORT == 5432
       assert settings.DB_USER == 'mestocker_user'
       assert settings.DB_PASSWORD == 'secure_password'
       assert settings.DB_NAME == 'mestocker_dev'

   @patch.dict(os.environ, {
       'DB_HOST': 'production-db',
       'DB_PORT': '5433',
       'DB_USER': 'prod_user',
       'DB_PASSWORD': 'prod_pass',
       'DB_NAME': 'mestocker_prod'
   })
   def test_individual_db_fields_from_env(self):
       """Test que verifica campos individuales desde entorno."""
       settings = Settings()

       assert settings.DB_HOST == 'production-db'
       assert settings.DB_PORT == 5433
       assert settings.DB_USER == 'prod_user'
       assert settings.DB_PASSWORD == 'prod_pass'
       assert settings.DB_NAME == 'mestocker_prod'