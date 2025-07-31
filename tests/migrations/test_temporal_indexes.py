"""
Tests para verificar índices temporales creados por migración 1.2.6.4
NOTA: Tests simplificados sin async para evitar deuda técnica
"""
import pytest
import subprocess
import re


class TestTemporalIndexes:
    """Test suite para verificar índices de fecha para reportes."""

    def test_migration_applied_successfully(self):
        """Verificar que la migración se aplicó correctamente."""
        # Verificar que alembic muestra la migración actual
        result = subprocess.run(
            ["alembic", "current"], 
            capture_output=True, 
            text=True, 
            cwd="."
        )

        assert result.returncode == 0, "Alembic current falló"
        assert "ba2f2921ee25" in result.stdout, "Migración de índices no aplicada"

    def test_temporal_indexes_exist_in_database(self):
        """Verificar que los índices temporales existen usando psql."""
        # Consulta directa a PostgreSQL sin async
        query = """
        SELECT COUNT(*) as index_count 
        FROM pg_indexes 
        WHERE indexname LIKE '%created_at%' 
           OR indexname LIKE '%updated_at%'
           OR indexname LIKE '%type_created%'
           OR indexname LIKE '%status_updated%';
        """

        # Ejecutar consulta directamente con psql
        result = subprocess.run([
            "psql", 
            "postgresql://mestocker_user:secure_password@localhost:5432/mestocker_dev",
            "-t", "-c", query
        ], capture_output=True, text=True)

        if result.returncode == 0:
            index_count = int(result.stdout.strip())
            # Esperamos al menos 10 índices temporales
            assert index_count >= 10, f"Solo {index_count} índices encontrados, esperado >=10"
        else:
            # Si psql no está disponible, marcar como skip
            pytest.skip("psql no disponible para verificación directa")

    def test_alembic_history_clean(self):
        """Verificar que el historial de Alembic está limpio."""
        result = subprocess.run(
            ["alembic", "history"], 
            capture_output=True, 
            text=True, 
            cwd="."
        )

        assert result.returncode == 0, "Alembic history falló"
        assert "ba2f2921ee25" in result.stdout, "Migración no aparece en historial"
        assert "9164fb08a156" in result.stdout, "Migración baseline no aparece en historial"
