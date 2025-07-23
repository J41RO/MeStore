# ~/tests/integration/test_api_versioning.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests de Integración para API Versioning
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_api_versioning.py
# Ruta: ~/tests/integration/test_api_versioning.py
# Autor: Jairo
# Fecha de Creación: 2025-07-23
# Última Actualización: 2025-07-23
# Versión: 1.1.0
# Propósito: Tests de integración para verificar API versioning correcto
#            Verifica que todos los endpoints estén bajo /api/v1/ y estructura correcta
#
# Modificaciones:
# 2025-07-23 - Corrección de test_health_ready_endpoint para manejar JSON anidado
# 2025-07-23 - Agregado encabezado estándar y limpieza de código
#
# ---------------------------------------------------------------------------------------------

"""
Tests de Integración para API Versioning v1
==========================================
Verifican que todos los endpoints estén correctamente montados bajo /api/v1/
y que no existan rutas sin versión.
"""

import ast
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Cliente de test para FastAPI
client = TestClient(app)


class TestAPIVersioning:
   """Test suite para verificar API versioning correcto."""

   def test_health_endpoint_v1_responds_200(self):
       """Verificar que /api/v1/health/health responde 200."""
       response = client.get("/api/v1/health/health")
       assert response.status_code == 200
       assert "status" in response.json()

   def test_health_ready_endpoint_v1_responds_200(self):
       """Verificar que /api/v1/health/ready responde 200 o 503 (servicios no disponibles)."""
       response = client.get("/api/v1/health/ready")
       assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}: {response.json()}"

       data = response.json()

       # Para respuesta 200: estructura directa
       if response.status_code == 200:
           assert 'status' in data, "200 response must have 'status' field"
           assert data['status'] == 'ready', "Status should be 'ready' for 200 response"

       # Para respuesta 503: FastAPI anida la respuesta en 'detail' como JSON string
       elif response.status_code == 503:
           assert 'detail' in data, "503 response must have 'detail' field"
           detail = ast.literal_eval(data['detail'])
           assert 'status' in detail, "503 response detail must have 'status' field"
           assert detail['status'] == 'not_ready', "Status should be 'not_ready' for 503 response"

   def test_logs_health_endpoint_v1_responds_200(self):
       """Verificar que /api/v1/logs/logs/health responde 200."""
       response = client.get("/api/v1/logs/logs/health")
       assert response.status_code == 200

   def test_all_endpoints_under_api_v1(self):
       """Verificar que todos los endpoints principales están bajo /api/v1/."""
       # Obtener todas las rutas de la aplicación
       routes = []
       for route in app.routes:
           if hasattr(route, 'path') and hasattr(route, 'methods'):
               routes.append((route.path, route.methods))

       # Filtrar rutas que deberían estar versionadas
       api_routes = [
           path for path, methods in routes 
           if any(keyword in path.lower() for keyword in [
               'logs', 'embeddings', 'fulfillment', 
               'marketplace', 'agents'
           ]) and not path.startswith('/docs') and not path.startswith('/openapi')
       ]

       # Verificar que todas están bajo /api/v1/
       non_versioned = [path for path in api_routes if not path.startswith('/api/v1/')]

       assert len(non_versioned) == 0, f"Rutas sin versión encontradas: {non_versioned}"
       assert len(api_routes) >= 15, f"Pocas rutas API encontradas: {len(api_routes)}"

   def test_no_routes_without_version(self):
       """Verificar que no existen rutas legacy sin versión."""
       # Rutas que NO deberían existir (sin versión)
       legacy_routes = [
           "/logs", 
           "/embeddings",
           "/fulfillment",
           "/marketplace",
           "/agents"
       ]

       for route_path in legacy_routes:
           response = client.get(route_path)
           # Debe devolver 404 porque estas rutas no deben existir
           assert response.status_code == 404, f"Ruta legacy {route_path} aún existe"

   def test_api_v1_prefix_consistency(self):
       """Verificar que todas las rutas v1 usan el prefijo consistentemente."""
       v1_routes = []
       for route in app.routes:
           if hasattr(route, 'path') and '/api/v1/' in route.path:
               v1_routes.append(route.path)

       # Verificar que todas las rutas v1 empiezan con /api/v1/
       for route_path in v1_routes:
           assert route_path.startswith('/api/v1/'), f"Ruta v1 mal formada: {route_path}"

       # Verificar que tenemos al menos las rutas principales
       expected_route_prefixes = [
           '/api/v1/health/',
           '/api/v1/logs/',
           '/api/v1/embeddings/',
       ]

       for expected_prefix in expected_route_prefixes:
           matching_routes = [r for r in v1_routes if r.startswith(expected_prefix)]
           assert len(matching_routes) > 0, f"No se encontraron rutas para {expected_prefix}"

   def test_openapi_docs_accessible(self):
       """Verificar que la documentación OpenAPI sigue siendo accesible."""
       response = client.get("/docs")
       assert response.status_code == 200

       response = client.get("/openapi.json")
       assert response.status_code == 200
       openapi_data = response.json()
       assert "paths" in openapi_data

       # Verificar que las rutas v1 aparecen en OpenAPI
       paths = openapi_data["paths"]
       v1_paths = [path for path in paths.keys() if "/api/v1/" in path]
       assert len(v1_paths) >= 10, f"Pocas rutas v1 en OpenAPI: {len(v1_paths)}"


@pytest.mark.integration
class TestSpecificEndpoints:
   """Tests específicos para endpoints críticos."""

   def test_health_complete_endpoints(self):
       """Verificar endpoints de health completo."""
       endpoints = [
           "/api/v1/health-complete/health/",
           "/api/v1/health-complete/health/redis", 
           "/api/v1/health-complete/health/database",
       ]

       for endpoint in endpoints:
           response = client.get(endpoint)
           assert response.status_code in [200, 503], f"Endpoint {endpoint} falló"

   def test_embeddings_endpoints_structure(self):
       """Verificar estructura de endpoints de embeddings."""
       # Test que los endpoints de embeddings siguen el patrón correcto
       test_collection = "test_collection"

       # Estos endpoints deben existir en la estructura (aunque fallen por lógica de negocio)
       endpoints_to_test = [
           f"/api/v1/embeddings/embeddings/{test_collection}/add",
           f"/api/v1/embeddings/embeddings/{test_collection}/query",
           f"/api/v1/embeddings/embeddings/{test_collection}/update",
       ]

       for endpoint in endpoints_to_test:
           # POST/PUT pueden fallar con 422 (validation error) pero no 404
           if "add" in endpoint or "update" in endpoint:
               response = client.post(endpoint, json={})
           else:
               response = client.post(endpoint, json={})

           assert response.status_code != 404, f"Endpoint {endpoint} no existe (404)"