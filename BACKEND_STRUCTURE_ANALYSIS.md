📊 MESTORE BACKEND - ESTRUCTURA CON COBERTURA DE TESTS
============================================================

🔍 LEYENDA:
✅ = Tiene tests | ❌ = Sin tests | 🔍 = Tests parciales
📊 = Cobertura conocida | 🏷️ = Tipos: unit/integration/e2e/api
🔥 = Prioridad alta | ⚠️ = Prioridad media | ℹ️ = Prioridad baja

app/
│   ├── __init__.py ✅ ℹ️ 🏷️[integration, unit, e2e]
│   │       📁 tests/e2e/app/test_main_endpoints_e2e.py ----------------------------------------------------✅ 16 PASSED
│   │       📁 tests/integration/app/test_main_middleware_integration.py------------------------------------✅ 16 PASSED
│   │       📁 tests/integration/test_admin_approval_processes_red.py---------------------------------------✅ 11 PASSED
│   │       📁 tests/unit/app/test_main_app_initialization.py-----------------------------------------------✅ 16 PASSED
│   ├── agents/
│   │   └── __init__.py ❌ ℹ️
│   ├── api/
│   │   ├── __init__.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/api/test_comisiones.py-------------------------------------------------------------✅ 04 PASSED
│   │   │       📁 tests/api/test_comisiones_detalle.py-----------------------------------------------------✅ 02 PASSED
│   │   │       📁 tests/api/test_comisiones_dispute.py-----------------------------------------------------✅ 04 PASSED
│   │   │       📁 tests/api/test_critical_endpoints_mvp.py-------------------------------------------------✅ 21 PASSED
│   │   │       📁 tests/api/test_health.py-----------------------------------------------------------------✅ 06 PASSED
│   │   │       📁 tests/api/test_incidentes.py-------------------------------------------------------------✅ 09 PASSED
│   │   │       📁 tests/api/test_inventory.py--------------------------------------------------------------✅ 09 PASSED
│   │   │       📁 tests/api/test_inventory_alertas.py------------------------------------------------------✅ 04 PASSED
│   │   │       📁 tests/api/test_inventory_reserva.py------------------------------------------------------✅ 02 PASSED
│   │   │       📁 tests/api/test_inventory_reserva_final.py------------------------------------------------✅ 02 PASSED
│   │   │       📁 tests/api/test_inventory_ubicacion_put.py------------------------------------------------✅ 02 PASSED
│   │   │       📁 tests/api/test_inventory_ubicaciones.py--------------------------------------------------✅ 03 PASSED
│   │   │       📁 tests/api/test_pagos_historial.py--------------------------------------------------------✅ 01 PASSED
│   │   │       📁 tests/api/test_perfil_bancarios.py-------------------------------------------------------✅ 03 PASSED
│   │   │       📁 tests/api/test_productos_upload.py-------------------------------------------------------✅ 03 PASSED
│   │   │       📁 tests/api/v1/deps/conftest.py------------------------------------------------------------ > Configuracion
│   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-------------------------------------✅ 25 PASSED
│   │   │       📁 tests/performance/test_critical_api_coverage.py------------------------------------------✅ 23 PASSED
│   │   │       📁 tests/test_api_embeddings.py-------------------------------------------------------------✅ 31 PASSED
│   │   │       📁 tests/test_api_id_consistency.py---------------------------------------------------------✅ 18 PASSED
│   │   └── v1/
│   │       ├── __init__.py ✅ ℹ️ 🏷️[api]
│   │       │       📁 tests/api/v1/deps/conftest.py-------------------------------------------------------- > Configuracion
│   │       │       📁 tests/api/v1/deps/test_database_deps_tdd.py------------------------------------------✅ 14 PASSED
│   │       │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py---------------------------------✅ 25 PASSED
│   │       ├── deps/
│   │       │   ├── __init__.py ✅ ℹ️ 🏷️[api]
│   │       │   │       📁 tests/api/v1/deps/conftest.py---------------------------------------------------- > Configuracion
│   │       │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py--------------------------------------✅ 14 PASSED
│   │       │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-----------------------------✅ 25 PASSED
│   │       │   ├── auth.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │       │   │       📁 tests/api/v1/deps/conftest.py---------------------------------------------------- > Configuracion
│   │       │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py--------------------------------------✅ 14 PASSED
│   │       │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-----------------------------✅ 25 PASSED
│   │       │   │       📁 tests/unit/admin_management/test_admin_auth_patterns_simple.py------------------- Framework enterprise-level para testing de auth/authz
│   │       │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py----------------✅ 08 PASSED
│   │       │   │       📁 tests/scripts/comprehensive_auth_test.py-[- Prueba completa del sistema de autenticación - Prueba completa del sistema de autenticación]
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py- [- Prueba directa de endpoints de login - Uso de aiohttp para peticiones async]
│   │       │   │       📁 tests/scripts/test_auth_integration.py-[- Valida comunicación entre frontend y backend - Pruebas de integración completa]
│   │       │   │       📁 tests/scripts/test_simple_auth.py-[- Prueba funciones de password directamente - Acceso directo a base de datos SQLite]
│   │       │   │       📁 tests/scripts/test_websocket_auth.py-[- Prueba autenticación en tiempo real - Testing de conexiones WebSocket]
│   │       │   │       📁 tests/services/test_auth_service.py----------------------------------------------✅ 13 PASSED
│   │       │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py------------------------✅ 12 PASSED
│   │       │   │       📁 tests/unit/auth/test_auth_service.py---------------------------------------------✅ 03 PASSED
│   │       │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py-------------------------------✅ 28 PASSED
│   │       │   │       📁 tests/unit/auth/test_auth_service_enhanced.py------------------------------------✅ 26 PASSED
│   │       │   │       📁 tests/unit/auth/test_auth_service_tdd.py-----------------------------------------✅ 18 PASSED
│   │       │   │       📁 tests/unit/auth/test_secure_auth_service.py--------------------------------------✅ 12 PASSED
│   │       │   │       📁 tests/unit/core/test_auth_tdd.py-------------------------------------------------✅ 36 PASSED
│   │       │   │       📁 tests/unit/core/test_integrated_auth_tdd.py--------------------------------------✅ 47 PASSED
│   │       │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py---------------------------------✅ 37 PASSED
│   │       │   │       📁 tests/unit/services/test_secure_auth_service.py---------------------------------- ❌ FAILED
│   │       │   │       📁 tests/unit/test_auth.py----------------------------------------------------------✅ 11 PASSED
│   │       │   │       📁 tests/unit/test_auth_dependency.py-----------------------------------------------✅ 08 PASSED
│   │       │   ├── database.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │       │   │       📁 tests/api/v1/deps/conftest.py---------------------------------------------------- > Configuracion
│   │       │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py--------------------------------------✅ 14 PASSED
│   │       │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-----------------------------✅ 25 PASSED
│   │       │   │       📁 tests/integration/admin_management/test_admin_database_integration.py------------ ❌ ERROR
│   │       │   │       📁 tests/test_database_config.py----------------------------------------------------✅ 07 PASSED
│   │       │   │       📁 tests/test_database_fixtures_validation.py---------------------------------------✅ 15 PASSED
│   │       │   │       📁 tests/test_database_indexes.py---------------------------------------------------✅ 06 PASSED
│   │       │   │       📁 tests/test_database_isolation.py-------------------------------------------------✅ 06 PASSED
│   │       │   │       📁 tests/test_database_working.py---------------------------------------------------✅ 10 PASSED
│   │       │   │       📁 tests/unit/test_database_dependency.py------------------------------------------- ❌ FAILED
│   │       │   └── standardized_auth.py ✅ ⚠️ 🏷️[api]
│   │       │           📁 tests/api/v1/deps/conftest.py
│   │       │           📁 tests/api/v1/deps/test_database_deps_tdd.py--------------------------------------✅ 14 PASSED
│   │       │           📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-----------------------------✅ 25 PASSED
│   │       ├── endpoints/
│   │       │   ├── admin.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py-----------------------------------------✅ 21 PASSED
│   │       │   │       📁 tests/e2e/admin_management/test_admin_security_flows.py--------------------------❌ ERROR
│   │       │   │       📁 tests/e2e/admin_management/test_admin_vendor_management.py-----------------------✅ 04 PASSED
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py-----------------------------------------✅ 16 PASSED
│   │       │   │       📁 tests/e2e/test_admin_file_upload_e2e_red.py--------------------------------------✅ 10 PASSED
│   │       │   │       📁 tests/e2e/test_admin_media_processing_e2e_red.py---------------------------------✅ 09 PASSED
│   │       │   │       📁 tests/fixtures/admin_management/admin_auth_test_patterns.py----------------------fixtures
│   │       │   │       📁 tests/fixtures/admin_management/admin_testing_fixtures.py------------------------fixtures
│   │       │   │       📁 tests/fixtures/admin_test_fixtures_refactored.py---------------------------------fixtures
│   │       │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py----------------✅ 08 PASSED
│   │       │   │       📁 tests/integration/admin_management/test_admin_cross_system_integration.py-------- ❌ ERROR
│   │       │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_integration_orchestrator.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_integration_runner.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_notification_integration.py-
│   │       │   │       📁 tests/integration/admin_management/test_admin_performance_integration.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_service_integration.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_session_integration.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_workflows.py
│   │       │   │       📁 tests/integration/conftest_admin_workflows_red.py
│   │       │   │       📁 tests/integration/test_admin_approval_processes_red.py
│   │       │   │       📁 tests/integration/test_admin_quality_assessment_red.py
│   │       │   │       📁 tests/integration/test_admin_verification_workflows_red.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin/conftest_admin_red.py
│   │       │   │       📁 tests/unit/admin/test_admin_dashboard_kpis_red.py
│   │       │   │       📁 tests/unit/admin/test_admin_qr_management_red.py
│   │       │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │       │   │       📁 tests/unit/admin/test_admin_storage_management_red.py
│   │       │   │       📁 tests/unit/admin/test_admin_workflow_verification_red.py
│   │       │   │       📁 tests/unit/admin_management/admin_test_fixtures.py
│   │       │   │       📁 tests/unit/admin_management/conftest_admin_user_management.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_data_management_red.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_comprehensive_red.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_green_phase.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_refactor_phase.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_monitoring_analytics_red.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_system_config_red.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_tdd_framework.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_user_management_red.py
│   │       │   │       📁 tests/unit/admin_management/test_comprehensive_admin_examples.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/core/test_admin_utils.py
│   │       │   ├── admin_management.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_comprehensive_red.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_green_phase.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_management_refactor_phase.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── admin_management_refactored.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── agents.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── alerts.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_alerts.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── auth.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-------------------------------------✅ 25 PASSED
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/fixtures/admin_management/admin_auth_test_patterns.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py---------------------✅ 08 PASSED
│   │       │   │       📁 tests/scripts/comprehensive_auth_test.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/scripts/test_auth_integration.py
│   │       │   │       📁 tests/scripts/test_simple_auth.py
│   │       │   │       📁 tests/scripts/test_websocket_auth.py
│   │       │   │       📁 tests/services/test_auth_service.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/auth/test_auth_service.py
│   │       │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py
│   │       │   │       📁 tests/unit/auth/test_auth_service_enhanced.py
│   │       │   │       📁 tests/unit/auth/test_auth_service_tdd.py
│   │       │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │       │   │       📁 tests/unit/core/test_auth_tdd.py
│   │       │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │       │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │       │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │       │   │       📁 tests/unit/test_auth.py
│   │       │   │       📁 tests/unit/test_auth_dependency.py-----------------------------------------------✅ 08 PASSED
│   │       │   ├── categories.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── comisiones.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_comisiones.py--------------------------------------------------✅ 04 PASSED
│   │       │   │       📁 tests/api/test_comisiones_detalle.py------------------------------------------✅ 02 PASSED
│   │       │   │       📁 tests/api/test_comisiones_dispute.py
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── commissions.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── embeddings.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_api_embeddings.py
│   │       │   │       📁 tests/test_embeddings.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── example_standardized.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── fulfillment.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_models_product_fulfillment.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │       │   ├── health.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/test_health.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/integration/test_health_robust.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_health.py
│   │       │   │       📁 tests/test_health_check.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── health_complete.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── inventory.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/test_inventory.py
│   │       │   │       📁 tests/api/test_inventory_alertas.py
│   │       │   │       📁 tests/api/test_inventory_reserva.py
│   │       │   │       📁 tests/api/test_inventory_reserva_final.py
│   │       │   │       📁 tests/api/test_inventory_ubicacion_put.py
│   │       │   │       📁 tests/api/test_inventory_ubicaciones.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_inventory_quality_fields.py
│   │       │   │       📁 tests/test_models_inventory.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/test_schemas_inventory.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/models/test_models_inventory.py
│   │       │   ├── leads.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── logs.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── marketplace.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── orders.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/services/test_notification_orders.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── pagos.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/test_pagos_historial.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── payments.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── perfil.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/test_perfil_bancarios.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── performance.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/integration/admin_management/test_admin_performance_integration.py
│   │       │   │       📁 tests/performance/test_performance_monitor.py
│   │       │   │       📁 tests/scripts/performance_e2e_tests.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/core/test_performance_middleware.py
│   │       │   ├── productos.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/api/test_productos_upload.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── products.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_simple.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── products_bulk.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_simple.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── search.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── secure_auth.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │       │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │       │   ├── system_config.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/integration/system/test_final_system_config.py
│   │       │   │       📁 tests/integration/system/test_system_config_integration.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_admin_system_config_red.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── vendedores.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/test_vendedores_login.py
│   │       │   │       📁 tests/test_vendedores_registro.py
│   │       │   │       📁 tests/test_vendedores_simple.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   ├── vendor_profile.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │   │       📁 tests/api/test_critical_endpoints_mvp.py
│   │       │   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │   │       📁 tests/scripts/test_auth_endpoints.py
│   │       │   │       📁 tests/test_products_bulk_endpoints.py
│   │       │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       │   └── websocket_analytics.py ✅ ⚠️ 🏷️[api, unit, e2e]
│   │       │           📁 tests/api/test_critical_endpoints_mvp.py
│   │       │           📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       │           📁 tests/scripts/test_auth_endpoints.py
│   │       │           📁 tests/test_products_bulk_endpoints.py
│   │       │           📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │       └── handlers/
│   │           ├── __init__.py ❌ ℹ️
│   │           └── exceptions.py ✅ ℹ️ 🏷️[api]
│   │                   📁 tests/test_final_exceptions.py
│   ├── core/
│   │   ├── admin_utils.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── auth.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-------------------------------------✅ 25 PASSED
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/fixtures/admin_management/admin_auth_test_patterns.py
│   │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py----------------------✅ 08 PASSED
│   │   │       📁 tests/scripts/comprehensive_auth_test.py
│   │   │       📁 tests/scripts/test_auth_endpoints.py
│   │   │       📁 tests/scripts/test_auth_integration.py
│   │   │       📁 tests/scripts/test_simple_auth.py
│   │   │       📁 tests/scripts/test_websocket_auth.py
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │   │       📁 tests/unit/auth/test_auth_service.py
│   │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py
│   │   │       📁 tests/unit/auth/test_auth_service_enhanced.py
│   │   │       📁 tests/unit/auth/test_auth_service_tdd.py
│   │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/test_auth.py
│   │   │       📁 tests/unit/test_auth_dependency.py-----------------------------------------------✅ 08 PASSED
│   │   ├── chromadb.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/test_chromadb.py
│   │   │       📁 tests/test_chromadb_integration.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── config.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/integration/system/test_final_system_config.py
│   │   │       📁 tests/integration/system/test_system_config_integration.py
│   │   │       📁 tests/test_config.py
│   │   │       📁 tests/test_database_config.py
│   │   │       📁 tests/unit/admin_management/test_admin_system_config_red.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── database.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │       📁 tests/test_database_config.py
│   │   │       📁 tests/test_database_fixtures_validation.py
│   │   │       📁 tests/test_database_indexes.py
│   │   │       📁 tests/test_database_isolation.py
│   │   │       📁 tests/test_database_working.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   │       📁 tests/unit/test_database_dependency.py
│   │   ├── dependencies.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/test_dependencies.py
│   │   │       📁 tests/test_dependencies_simple.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── dependencies_simple.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/test_dependencies_simple.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── id_validation.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── integrated_auth.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── integrated_logging_system.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── logger.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/test_logger_loguru.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── logging_rotation.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── middleware/
│   │   │   └── ip_detection.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │           📁 tests/integration/app/test_main_middleware_integration.py
│   │   │           📁 tests/unit/core/test_performance_middleware.py
│   │   │           📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │           📁 tests/unit/test_ip_detection.py
│   │   │           📁 tests/unit/test_logging_middleware.py
│   │   ├── middleware_integration.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── middleware_integration_simple.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── performance_middleware.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── redis/
│   │   │   ├── __init__.py ✅ ℹ️ 🏷️[api, unit]
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   ├── base.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │   │       📁 tests/test_base_simple.py
│   │   │   │       📁 tests/test_database_config.py
│   │   │   │       📁 tests/test_database_fixtures_validation.py
│   │   │   │       📁 tests/test_database_indexes.py
│   │   │   │       📁 tests/test_database_isolation.py
│   │   │   │       📁 tests/test_database_working.py
│   │   │   │       📁 tests/unit/auth/test_role_based_access.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   │       📁 tests/unit/test_database_dependency.py
│   │   │   ├── cache.py ✅ ℹ️ 🏷️[api, unit]
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   ├── dependencies.py ✅ ℹ️ 🏷️[api, unit]
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/test_dependencies.py
│   │   │   │       📁 tests/test_dependencies_simple.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │   ├── queue.py ✅ ℹ️ 🏷️[api, unit]
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/scripts/insert_test_queue_data.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   ├── service.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │   │       📁 tests/conftest_redis_override.py
│   │   │   │       📁 tests/integration/admin_management/test_admin_service_integration.py
│   │   │   │       📁 tests/services/test_auth_service.py
│   │   │   │       📁 tests/services/test_order_state_service.py
│   │   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │   │       📁 tests/test_wompi_service_methods.py
│   │   │   │       📁 tests/unit/auth/test_auth_service.py
│   │   │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py
│   │   │   │       📁 tests/unit/auth/test_auth_service_enhanced.py
│   │   │   │       📁 tests/unit/auth/test_auth_service_tdd.py
│   │   │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │   └── session.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │           📁 tests/conftest_redis_override.py
│   │   │           📁 tests/integration/admin_management/test_admin_session_integration.py
│   │   │           📁 tests/unit/core/redis/test_cache.py
│   │   │           📁 tests/unit/core/redis/test_queue.py
│   │   │           📁 tests/unit/core/redis/test_service.py
│   │   │           📁 tests/unit/database/test_session.py
│   │   │           📁 tests/unit/database/test_session_standalone.py
│   │   ├── responses.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── secret_manager.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── security.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/e2e/admin_management/test_admin_security_flows.py
│   │   │       📁 tests/e2e/admin_management/test_crisis_security_management.py
│   │   │       📁 tests/integration/test_cors_security.py
│   │   │       📁 tests/scripts/security_penetration_tests.py
│   │   │       📁 tests/scripts/security_validation_test.py
│   │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │   │       📁 tests/unit/auth/test_jwt_security.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   │       📁 tests/unit/test_security.py
│   │   │       📁 tests/unit/test_security_headers.py
│   │   ├── system_integration_validator.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   ├── types.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/core/test_config.py
│   │   │       📁 tests/unit/core/redis/test_cache.py
│   │   │       📁 tests/unit/core/redis/test_queue.py
│   │   │       📁 tests/unit/core/redis/test_service.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/core/test_types.py
│   │   │       📁 tests/unit/core/test_types_simple.py
│   │   └── unified_error_handler.py ✅ ℹ️ 🏷️[api, unit]
│   │           📁 tests/core/test_config.py
│   │           📁 tests/unit/core/redis/test_cache.py
│   │           📁 tests/unit/core/redis/test_queue.py
│   │           📁 tests/unit/core/redis/test_service.py
│   │           📁 tests/unit/core/test_admin_utils.py
│   │           📁 tests/unit/core/test_auth_tdd.py
│   │           📁 tests/unit/core/test_dependencies_simple_tdd.py
│   │           📁 tests/unit/core/test_integrated_auth_tdd.py
│   │           📁 tests/unit/core/test_performance_middleware.py
│   │           📁 tests/unit/core/test_security_tdd.py
│   │           📁 tests/unit/core/test_types.py
│   │           📁 tests/unit/core/test_types_simple.py
│   ├── database/
│   │   ├── __init__.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │       📁 tests/test_database_config.py
│   │   │       📁 tests/test_database_fixtures_validation.py
│   │   │       📁 tests/test_database_indexes.py
│   │   │       📁 tests/test_database_isolation.py
│   │   │       📁 tests/test_database_working.py
│   │   │       📁 tests/unit/database/test_session.py
│   │   │       📁 tests/unit/database/test_session_standalone.py
│   │   │       📁 tests/unit/test_database_dependency.py
│   │   └── session.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │           📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │           📁 tests/integration/admin_management/test_admin_database_integration.py
│   │           📁 tests/integration/admin_management/test_admin_session_integration.py
│   │           📁 tests/test_database_config.py
│   │           📁 tests/test_database_fixtures_validation.py
│   │           📁 tests/test_database_indexes.py
│   │           📁 tests/test_database_isolation.py
│   │           📁 tests/test_database_working.py
│   │           📁 tests/unit/database/test_session.py
│   │           📁 tests/unit/database/test_session_standalone.py
│   │           📁 tests/unit/test_database_dependency.py
│   ├── fulfillment/
│   │   └── __init__.py ✅ ℹ️ 🏷️[api, unit]
│   │           📁 tests/test_models_product_fulfillment.py
│   │           📁 tests/unit/models/test_models_product_fulfillment.py
│   ├── main.py ✅ ⚠️ 🏷️[integration, unit, e2e]
│   │       📁 tests/e2e/app/test_main_endpoints_e2e.py
│   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │       📁 tests/integration/test_admin_approval_processes_red.py
│   │       📁 tests/unit/app/test_main_app_initialization.py
│   ├── marketplace/
│   │   └── __init__.py ❌ ℹ️
│   ├── middleware/
│   │   ├── __init__.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── auth_rate_limiting.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── comprehensive_security.py ✅ ⚠️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── enterprise_security.py ✅ ⚠️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── logging.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── performance_monitor.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/performance/test_performance_monitor.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── performance_optimization.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── rate_limiter.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   │       📁 tests/unit/test_rate_limiter.py
│   │   ├── rate_limiting.py ✅ ℹ️ 🏷️[integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── response_standardization.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/scripts/test_response_standardization.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   ├── security.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │   │       📁 tests/e2e/admin_management/test_admin_security_flows.py
│   │   │       📁 tests/e2e/admin_management/test_crisis_security_management.py
│   │   │       📁 tests/integration/app/test_main_middleware_integration.py
│   │   │       📁 tests/integration/test_cors_security.py
│   │   │       📁 tests/scripts/security_penetration_tests.py
│   │   │       📁 tests/scripts/security_validation_test.py
│   │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │   │       📁 tests/unit/auth/test_jwt_security.py
│   │   │       📁 tests/unit/core/test_performance_middleware.py
│   │   │       📁 tests/unit/core/test_security_tdd.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/test_logging_middleware.py
│   │   │       📁 tests/unit/test_security.py
│   │   │       📁 tests/unit/test_security_headers.py
│   │   └── user_agent_validator.py ✅ ℹ️ 🏷️[integration, unit]
│   │           📁 tests/integration/app/test_main_middleware_integration.py
│   │           📁 tests/unit/core/test_performance_middleware.py
│   │           📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │           📁 tests/unit/test_logging_middleware.py
│   │           📁 tests/unit/test_user_agent_validator.py
│   ├── models/
│   │   ├── __init__.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── admin_activity_log.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── admin_permission.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── base.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_base_simple.py
│   │   │       📁 tests/test_database_config.py
│   │   │       📁 tests/test_database_fixtures_validation.py
│   │   │       📁 tests/test_database_indexes.py
│   │   │       📁 tests/test_database_isolation.py
│   │   │       📁 tests/test_database_working.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/auth/test_role_based_access.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/test_database_dependency.py
│   │   ├── category.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── commission.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_transaction_commission.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   ├── commission_dispute.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── discrepancy_report.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/integration/workflow/test_discrepancy_reports_system.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── incidente_inventario.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── incoming_product_queue.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── inventory.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/api/test_inventory.py
│   │   │       📁 tests/api/test_inventory_alertas.py
│   │   │       📁 tests/api/test_inventory_reserva.py
│   │   │       📁 tests/api/test_inventory_reserva_final.py
│   │   │       📁 tests/api/test_inventory_ubicacion_put.py
│   │   │       📁 tests/api/test_inventory_ubicaciones.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_inventory_quality_fields.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── inventory_audit.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── movement_tracker.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/integration/system/test_movement_tracker_integration.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── movimiento_stock.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── order.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── payment.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   ├── payout_history.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── payout_request.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── product.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/test_productos_upload.py
│   │   │       📁 tests/integration/workflow/test_e2e_production_readiness.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_products_bulk_endpoints.py
│   │   │       📁 tests/test_products_bulk_simple.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── product_image.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── storage.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_storage.py
│   │   │       📁 tests/test_storage_contracts.py
│   │   │       📁 tests/test_storage_manager.py
│   │   │       📁 tests/test_storage_relationships.py
│   │   │       📁 tests/unit/admin/test_admin_storage_management_red.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── system_setting.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── transaction.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_transaction.py
│   │   │       📁 tests/test_transaction_commission.py
│   │   │       📁 tests/test_transaction_status.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   ├── user.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │   │       📁 tests/e2e/admin_management/test_superuser_complete_workflows.py
│   │   │       📁 tests/integration/workflows/test_user_journeys.py
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/scripts/create_test_users.py
│   │   │       📁 tests/scripts/create_test_users_simple.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_user_colombian_fields.py
│   │   │       📁 tests/test_user_profile_fields.py
│   │   │       📁 tests/test_user_roles_verification.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/test_user_status_fields.py
│   │   │       📁 tests/unit/admin_management/conftest_admin_user_management.py
│   │   │       📁 tests/unit/admin_management/test_admin_user_management_red.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/test_user_agent_validator.py
│   │   ├── vendor_audit.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   ├── vendor_document.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/models/test_payment.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   └── vendor_note.py ✅ ⚠️ 🏷️[api, unit]
│   │           📁 tests/models/test_category_model_comprehensive_tdd.py
│   │           📁 tests/models/test_order.py
│   │           📁 tests/models/test_payment.py
│   │           📁 tests/models/test_product_model_comprehensive_tdd.py
│   │           📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │           📁 tests/models/test_system_setting_model_comprehensive_tdd.py
│   │           📁 tests/models/test_user.py
│   │           📁 tests/test_models_inventory.py
│   │           📁 tests/test_models_product.py
│   │           📁 tests/test_models_product_fulfillment.py
│   │           📁 tests/test_models_product_status.py
│   │           📁 tests/test_models_transaction.py
│   │           📁 tests/unit/models/test_models_inventory.py
│   │           📁 tests/unit/models/test_models_product.py
│   │           📁 tests/unit/models/test_models_product_fulfillment.py
│   │           📁 tests/unit/models/test_models_product_status.py
│   │           📁 tests/unit/models/test_models_transaction.py
│   │           📁 tests/unit/models/test_user_model_comprehensive.py
│   ├── schemas/
│   │   ├── __init__.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── admin.py ✅ ℹ️ 🏷️[api, integration, unit, e2e]
│   │   │       📁 tests/e2e/admin_management/test_admin_security_flows.py
│   │   │       📁 tests/e2e/admin_management/test_admin_vendor_management.py
│   │   │       📁 tests/e2e/test_admin_file_upload_e2e_red.py
│   │   │       📁 tests/e2e/test_admin_media_processing_e2e_red.py
│   │   │       📁 tests/fixtures/admin_management/admin_auth_test_patterns.py
│   │   │       📁 tests/fixtures/admin_management/admin_testing_fixtures.py
│   │   │       📁 tests/fixtures/admin_test_fixtures_refactored.py
│   │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py----------------------✅ 08 PASSED
│   │   │       📁 tests/integration/admin_management/test_admin_cross_system_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_integration_orchestrator.py
│   │   │       📁 tests/integration/admin_management/test_admin_integration_runner.py
│   │   │       📁 tests/integration/admin_management/test_admin_notification_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_performance_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_service_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_session_integration.py
│   │   │       📁 tests/integration/admin_management/test_admin_workflows.py
│   │   │       📁 tests/integration/conftest_admin_workflows_red.py
│   │   │       📁 tests/integration/test_admin_approval_processes_red.py
│   │   │       📁 tests/integration/test_admin_quality_assessment_red.py
│   │   │       📁 tests/integration/test_admin_verification_workflows_red.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/admin/conftest_admin_red.py
│   │   │       📁 tests/unit/admin/test_admin_dashboard_kpis_red.py
│   │   │       📁 tests/unit/admin/test_admin_qr_management_red.py
│   │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │   │       📁 tests/unit/admin/test_admin_storage_management_red.py
│   │   │       📁 tests/unit/admin/test_admin_workflow_verification_red.py
│   │   │       📁 tests/unit/admin_management/admin_test_fixtures.py
│   │   │       📁 tests/unit/admin_management/conftest_admin_user_management.py
│   │   │       📁 tests/unit/admin_management/test_admin_data_management_red.py
│   │   │       📁 tests/unit/admin_management/test_admin_management_comprehensive_red.py
│   │   │       📁 tests/unit/admin_management/test_admin_management_green_phase.py
│   │   │       📁 tests/unit/admin_management/test_admin_management_refactor_phase.py
│   │   │       📁 tests/unit/admin_management/test_admin_monitoring_analytics_red.py
│   │   │       📁 tests/unit/admin_management/test_admin_system_config_red.py
│   │   │       📁 tests/unit/admin_management/test_admin_tdd_framework.py
│   │   │       📁 tests/unit/admin_management/test_admin_user_management_red.py
│   │   │       📁 tests/unit/admin_management/test_comprehensive_admin_examples.py
│   │   │       📁 tests/unit/admin_management/test_tdd_admin_endpoints.py
│   │   │       📁 tests/unit/core/test_admin_utils.py
│   │   ├── alerts.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_alerts.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── auth.py ✅ ⚠️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_standardized_auth_deps_tdd.py-------------------------------------✅ 25 PASSED
│   │   │       📁 tests/fixtures/admin_management/admin_auth_test_patterns.py
│   │   │       📁 tests/integration/admin_management/test_admin_auth_integration.py------------------------✅ 08 PASSED
│   │   │       📁 tests/scripts/comprehensive_auth_test.py
│   │   │       📁 tests/scripts/test_auth_endpoints.py
│   │   │       📁 tests/scripts/test_auth_integration.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/scripts/test_simple_auth.py
│   │   │       📁 tests/scripts/test_websocket_auth.py
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/admin/test_admin_security_authorization_red.py
│   │   │       📁 tests/unit/auth/test_auth_service.py
│   │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py
│   │   │       📁 tests/unit/auth/test_auth_service_enhanced.py
│   │   │       📁 tests/unit/auth/test_auth_service_tdd.py
│   │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │   │       📁 tests/unit/core/test_auth_tdd.py
│   │   │       📁 tests/unit/core/test_integrated_auth_tdd.py
│   │   │       📁 tests/unit/middleware/test_auth_rate_limiting.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/test_auth.py
│   │   │       📁 tests/unit/test_auth_dependency.py-----------------------------------------------✅ 08 PASSED
│   │   ├── base.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│   │   │       📁 tests/integration/admin_management/test_admin_database_integration.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_base_simple.py
│   │   │       📁 tests/test_database_config.py
│   │   │       📁 tests/test_database_fixtures_validation.py
│   │   │       📁 tests/test_database_indexes.py
│   │   │       📁 tests/test_database_isolation.py
│   │   │       📁 tests/test_database_working.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/auth/test_role_based_access.py
│   │   │       📁 tests/unit/test_database_dependency.py
│   │   ├── category.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/models/test_category_model_comprehensive_tdd.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── commission.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_transaction_commission.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   ├── commission_dispute.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── common.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── embeddings_schemas.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── financial_reports.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_financial_reports.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── inventory.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/api/test_inventory.py
│   │   │       📁 tests/api/test_inventory_alertas.py
│   │   │       📁 tests/api/test_inventory_reserva.py
│   │   │       📁 tests/api/test_inventory_reserva_final.py
│   │   │       📁 tests/api/test_inventory_ubicacion_put.py
│   │   │       📁 tests/api/test_inventory_ubicaciones.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_inventory_quality_fields.py
│   │   │       📁 tests/test_models_inventory.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/models/test_models_inventory.py
│   │   ├── inventory_audit.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── leads.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── order.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/models/test_order.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── payout_history.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── payout_request.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── product.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/api/test_productos_upload.py
│   │   │       📁 tests/integration/workflow/test_e2e_production_readiness.py
│   │   │       📁 tests/models/test_product_model_comprehensive_tdd.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_models_product.py
│   │   │       📁 tests/test_models_product_fulfillment.py
│   │   │       📁 tests/test_models_product_status.py
│   │   │       📁 tests/test_products_bulk_endpoints.py
│   │   │       📁 tests/test_products_bulk_simple.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/models/test_models_product.py
│   │   │       📁 tests/unit/models/test_models_product_fulfillment.py
│   │   │       📁 tests/unit/models/test_models_product_status.py
│   │   ├── product_image.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── product_verification.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── response_base.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── search.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   ├── storage.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/models/test_storage_model_comprehensive_tdd.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_storage.py
│   │   │       📁 tests/test_storage_contracts.py
│   │   │       📁 tests/test_storage_manager.py
│   │   │       📁 tests/test_storage_relationships.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/admin/test_admin_storage_management_red.py
│   │   ├── system_config.py ✅ ℹ️ 🏷️[api, integration, unit]
│   │   │       📁 tests/integration/system/test_final_system_config.py
│   │   │       📁 tests/integration/system/test_system_config_integration.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/admin_management/test_admin_system_config_red.py
│   │   ├── transaction.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_models_transaction.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_transaction.py
│   │   │       📁 tests/test_transaction_commission.py
│   │   │       📁 tests/test_transaction_status.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/unit/models/test_models_transaction.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   ├── user.py ✅ ⚠️ 🏷️[api, integration, unit, e2e]
│   │   │       📁 tests/e2e/admin_management/test_superuser_complete_workflows.py
│   │   │       📁 tests/integration/workflows/test_user_journeys.py
│   │   │       📁 tests/models/test_user.py
│   │   │       📁 tests/scripts/create_test_users.py
│   │   │       📁 tests/scripts/create_test_users_simple.py
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_colombian_fields.py
│   │   │       📁 tests/test_user_profile_fields.py
│   │   │       📁 tests/test_user_roles_verification.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/test_user_status_fields.py
│   │   │       📁 tests/unit/admin_management/conftest_admin_user_management.py
│   │   │       📁 tests/unit/admin_management/test_admin_user_management_red.py
│   │   │       📁 tests/unit/models/test_user_model_comprehensive.py
│   │   │       📁 tests/unit/test_user_agent_validator.py
│   │   ├── vendedor.py ✅ ℹ️ 🏷️[api, unit]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   │       📁 tests/test_vendedor_celular_validation.py
│   │   │       📁 tests/test_vendedor_dashboard.py
│   │   │       📁 tests/test_vendedores_login.py
│   │   │       📁 tests/test_vendedores_registro.py
│   │   │       📁 tests/test_vendedores_simple.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── vendor_document.py ✅ ℹ️ 🏷️[api]
│   │   │       📁 tests/scripts/test_pydantic_v2_schemas.py
│   │   │       📁 tests/test_schemas_inventory.py
│   │   │       📁 tests/test_schemas_product.py
│   │   │       📁 tests/test_user_schemas_refactored.py
│   │   └── vendor_profile.py ✅ ℹ️ 🏷️[api]
│   │           📁 tests/scripts/test_pydantic_v2_schemas.py
│   │           📁 tests/test_schemas_inventory.py
│   │           📁 tests/test_schemas_product.py
│   │           📁 tests/test_user_schemas_refactored.py
│   ├── services/
│   │   ├── __init__.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── admin_permission_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── analytics_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── audit_logging_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── audit_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── auth_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/auth/test_auth_service.py
│   │   │       📁 tests/unit/auth/test_auth_service_comprehensive.py
│   │   │       📁 tests/unit/auth/test_auth_service_enhanced.py
│   │   │       📁 tests/unit/auth/test_auth_service_tdd.py
│   │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── cache_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── category_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── chroma_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── commission_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── database_optimization_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── discrepancy_analyzer.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── email_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── embedding_sync_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── embeddings.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/test_api_embeddings.py
│   │   │       📁 tests/test_embeddings.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── fraud_detection_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── integrated_payment_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── integrated_performance_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── inventory_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── jwt_blacklist_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── location_assignment_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── notification_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── order_notification_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── order_state_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── order_tracking_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── otp_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── payment_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── payments/
│   │   │   ├── __init__.py ✅ ⚠️ 🏷️[unit]
│   │   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   │   │       📁 tests/unit/payments/test_webhook_handler.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   ├── fraud_detection_service.py ✅ ⚠️ 🏷️[unit]
│   │   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   │   │       📁 tests/unit/payments/test_webhook_handler.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   ├── payment_commission_service.py ✅ ⚠️ 🏷️[unit]
│   │   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   │   │       📁 tests/unit/payments/test_webhook_handler.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   ├── payment_processor.py ✅ ⚠️ 🏷️[unit]
│   │   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   │   │       📁 tests/unit/payments/test_webhook_handler.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   ├── webhook_handler.py ✅ ⚠️ 🏷️[unit]
│   │   │   │       📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │   │       📁 tests/unit/payments/test_payment_processor.py
│   │   │   │       📁 tests/unit/payments/test_webhook_handler.py
│   │   │   │       📁 tests/unit/payments/test_wompi_service.py
│   │   │   └── wompi_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │           📁 tests/test_wompi_service_methods.py
│   │   │           📁 tests/unit/payments/test_payment_commission_integration.py
│   │   │           📁 tests/unit/payments/test_payment_processor.py
│   │   │           📁 tests/unit/payments/test_webhook_handler.py
│   │   │           📁 tests/unit/payments/test_wompi_service.py
│   │   ├── performance_monitoring_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── product_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── product_verification_workflow.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── qr_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── queue_notification_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── rate_limiting_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── search_analytics_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── search_cache_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── search_performance_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── search_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── secure_auth_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/auth/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── secure_session_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── security_validation_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── session_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── sms_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── space_optimizer_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── storage_manager_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   ├── transaction_service.py ✅ ⚠️ 🏷️[api, unit]
│   │   │       📁 tests/services/test_auth_service.py
│   │   │       📁 tests/services/test_notification_orders.py
│   │   │       📁 tests/services/test_order_state_service.py
│   │   │       📁 tests/services/test_order_tracking_service.py
│   │   │       📁 tests/unit/services/financial/test_commission_service.py
│   │   │       📁 tests/unit/services/financial/test_transaction_service.py
│   │   │       📁 tests/unit/services/test_async_vendedor.py
│   │   │       📁 tests/unit/services/test_async_vendedor_fixed.py
│   │   │       📁 tests/unit/services/test_commission_service_basic.py
│   │   │       📁 tests/unit/services/test_secure_auth_service.py
│   │   │       📁 tests/unit/services/test_simple_vendedor.py
│   │   │       📁 tests/unit/services/test_vendedor_final.py
│   │   └── vendor_service.py ✅ ⚠️ 🏷️[api, unit]
│   │           📁 tests/services/test_auth_service.py
│   │           📁 tests/services/test_notification_orders.py
│   │           📁 tests/services/test_order_state_service.py
│   │           📁 tests/services/test_order_tracking_service.py
│   │           📁 tests/unit/services/financial/test_commission_service.py
│   │           📁 tests/unit/services/financial/test_transaction_service.py
│   │           📁 tests/unit/services/test_async_vendedor.py
│   │           📁 tests/unit/services/test_async_vendedor_fixed.py
│   │           📁 tests/unit/services/test_commission_service_basic.py
│   │           📁 tests/unit/services/test_secure_auth_service.py
│   │           📁 tests/unit/services/test_simple_vendedor.py
│   │           📁 tests/unit/services/test_vendedor_final.py
│   ├── tasks/
│   │   └── queue_scheduler.py ❌ ℹ️
│   └── utils/
│       ├── __init__.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── benchmark.py ✅ ℹ️ 🏷️[api, unit]
│       │       📁 tests/performance/test_benchmark_tools.py
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── crud.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── crud_sync.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── database.py ✅ ℹ️ 🏷️[api, integration, unit]
│       │       📁 tests/api/v1/deps/test_database_deps_tdd.py----------------------------------------------✅ 14 PASSED
│       │       📁 tests/integration/admin_management/test_admin_database_integration.py
│       │       📁 tests/test_database_config.py
│       │       📁 tests/test_database_fixtures_validation.py
│       │       📁 tests/test_database_indexes.py
│       │       📁 tests/test_database_isolation.py
│       │       📁 tests/test_database_working.py
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_database_dependency.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── database_utils.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── file_validator.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── password.py ✅ ℹ️ 🏷️[api, unit]
│       │       📁 tests/scripts/test_password_functions.py
│       │       📁 tests/scripts/test_password_verification.py
│       │       📁 tests/scripts/update_test_passwords.py
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── query_analyzer.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── response_utils.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       ├── url_helper.py ✅ ℹ️ 🏷️[unit]
│       │       📁 tests/unit/core/test_admin_utils.py
│       │       📁 tests/unit/test_crud_utils_clean.py
│       │       📁 tests/unit/test_password_utils.py
│       └── validators.py ✅ ℹ️ 🏷️[unit]
│               📁 tests/unit/core/test_admin_utils.py
│               📁 tests/unit/test_crud_utils_clean.py
│               📁 tests/unit/test_password_utils.py

📈 RESUMEN EJECUTIVO DE COBERTURA
==================================================
📊 Total archivos fuente: 209
✅ Archivos con tests: 205 (98.1%)
❌ Archivos sin tests: 4 (1.9%)
🔥 Archivos críticos sin tests: 0

🏷️ DISTRIBUCIÓN TIPOS DE TESTS:
   unit: 182 archivos
   integration: 45 archivos
   e2e: 39 archivos
   api: 179 archivos


💡 RECOMENDACIONES:
1. Priorizar tests para archivos críticos marcados con 🔥
2. Implementar tests de integración para servicios complejos
3. Añadir tests E2E para flujos de usuario principales
4. Mantener cobertura >80% en módulos core

⚡ COMANDOS ÚTILES:
```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Generar reporte de cobertura
python -m pytest --cov=app --cov-report=html tests/

# Ejecutar solo tests unitarios
python -m pytest tests/unit/ -v

# Ejecutar tests con marcadores TDD
python -m pytest -m "tdd" -v
```