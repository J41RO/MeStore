#!/usr/bin/env python3
"""
Análisis completo de tests por criticidad
"""
import os
import re
from pathlib import Path

def categorizar_tests():
    """Categoriza todos los tests por nivel de criticidad"""

    # NIVEL CRÍTICO 1: Tests fundamentales que no pueden fallar
    criticos_nivel_1 = [
        # Core de la aplicación
        "tests/test_database_working.py",
        "tests/unit/test_final_success.py",
        "tests/api/test_health.py",
        "tests/core/test_config.py",
        "tests/test_config.py",

        # Autenticación básica
        "tests/unit/auth/test_auth_service.py",
        "tests/services/test_auth_service.py",
        "tests/unit/test_auth_dependency.py",
        "tests/unit/auth/test_secure_auth_service.py",
        "tests/security/test_jwt_encryption_standards.py",

        # Modelos fundamentales
        "tests/test_models_user.py",
        "tests/unit/models/test_models_user.py",
        "tests/unit/models/test_user_model.py",
        "tests/models/test_user.py",

        # Database core
        "tests/test_database_config.py",
        "tests/test_database_isolation.py",
        "tests/unit/database/test_session.py",
        "tests/database_test_config.py",
    ]

    # NIVEL CRÍTICO 2: Funcionalidad core del negocio
    criticos_nivel_2 = [
        # Vendedores (core business)
        "tests/test_vendedores_login.py",
        "tests/test_vendedores_registro.py",
        "tests/unit/services/test_vendedor_final.py",

        # Productos básicos
        "tests/test_models_product.py",
        "tests/unit/models/test_models_product.py",
        "tests/test_schemas_product.py",

        # Inventario básico
        "tests/test_models_inventory.py",
        "tests/unit/models/test_models_inventory.py",
        "tests/test_schemas_inventory.py",
        "tests/api/test_inventory.py",

        # Transacciones y pagos básicos
        "tests/test_models_transaction.py",
        "tests/models/test_payment.py",
        "tests/test_transaction.py",
        "tests/unit/models/test_models_transaction.py",

        # Admin management (ya validado)
        "tests/unit/admin_management/test_tdd_admin_endpoints.py",
    ]

    # NIVEL CRÍTICO 3: Funcionalidad importante
    criticos_nivel_3 = [
        # APIs críticas
        "tests/api/test_critical_endpoints_mvp.py",
        "tests/api/test_productos_upload.py",
        "tests/api/test_comisiones.py",
        "tests/api/test_pagos_historial.py",

        # Integración de sistemas
        "tests/integration/system/test_final_verification.py",
        "tests/integration/system/test_sistema_completo.py",
        "tests/integration/workflows/test_user_journeys.py",

        # E2E básico
        "tests/e2e/test_foundation_simple.py",
        "tests/e2e_comprehensive_test.py",

        # Servicios importantes
        "tests/unit/services/financial/test_commission_service.py",
        "tests/unit/services/financial/test_transaction_service.py",
        "tests/services/test_order_state_service.py",
    ]

    # NIVEL CRÍTICO 4: Funcionalidad secundaria
    criticos_nivel_4 = [
        # Storage y ubicaciones
        "tests/test_storage.py",
        "tests/test_storage_manager.py",
        "tests/test_location_assignment.py",
        "tests/api/test_inventory_ubicaciones.py",

        # QR y alertas
        "tests/test_qr_system.py",
        "tests/test_alerts.py",
        "tests/api/test_inventory_alertas.py",

        # Comisiones detalladas
        "tests/api/test_comisiones_detalle.py",
        "tests/api/test_comisiones_dispute.py",
        "tests/api/test_perfil_bancarios.py",

        # Admin avanzado
        "tests/unit/admin_management/test_admin_data_management_red.py",
        "tests/unit/admin_management/test_admin_management_green_phase.py",
        "tests/unit/admin/test_admin_dashboard_kpis_red.py",
    ]

    # NIVEL CRÍTICO 5: Testing y debugging
    criticos_nivel_5 = [
        # Utils y herramientas
        "tests/test_dependencies.py",
        "tests/test_fixtures_validation.py",
        "tests/unit/test_working_utilities.py",
        "tests/unit/test_crud_utils_clean.py",

        # Debugging tools
        "tests/debugging/test_log_rotation.py",
        "tests/debugging/test_logging_fixed.py",
        "tests/test_logger_loguru.py",

        # Performance y benchmarks
        "tests/performance/test_performance_monitor.py",
        "tests/performance/test_benchmark_tools.py",
        "tests/test_api_id_consistency.py",
    ]

    # NIVEL CRÍTICO 6: Tests experimentales y edge cases
    criticos_nivel_6 = [
        # Async y edge cases
        "tests/test_async_final.py",
        "tests/test_async_sync_fix_complete.py",
        "tests/test_final_exceptions.py",

        # Encoding y UTF8
        "tests/misc/test_encoding.py",
        "tests/misc/test_utf8.py",
        "tests/misc/test_extreme_utf8.py",

        # Integration experimental
        "tests/test_chromadb_integration.py",
        "tests/test_api_embeddings.py",
        "tests/test_embeddings.py",

        # E2E experimental
        "tests/e2e/admin_management/test_admin_security_flows.py",
        "tests/scripts/performance_e2e_tests.py",
    ]

    return {
        "CRÍTICO NIVEL 1 - CORE FUNDAMENTAL": criticos_nivel_1,
        "CRÍTICO NIVEL 2 - BUSINESS CORE": criticos_nivel_2,
        "CRÍTICO NIVEL 3 - FUNCIONALIDAD IMPORTANTE": criticos_nivel_3,
        "CRÍTICO NIVEL 4 - FUNCIONALIDAD SECUNDARIA": criticos_nivel_4,
        "CRÍTICO NIVEL 5 - TOOLS & DEBUGGING": criticos_nivel_5,
        "CRÍTICO NIVEL 6 - EXPERIMENTAL & EDGE CASES": criticos_nivel_6,
    }

def verificar_existencia_archivos():
    """Verifica que archivos existen realmente"""
    categorias = categorizar_tests()
    resultado = {}

    for categoria, tests in categorias.items():
        tests_existentes = []
        tests_no_existentes = []

        for test_file in tests:
            if os.path.exists(test_file):
                tests_existentes.append(test_file)
            else:
                tests_no_existentes.append(test_file)

        resultado[categoria] = {
            "existentes": tests_existentes,
            "no_existentes": tests_no_existentes,
            "total": len(tests),
            "existentes_count": len(tests_existentes)
        }

    return resultado

def generar_reporte():
    """Genera reporte completo de tests por criticidad"""
    resultado = verificar_existencia_archivos()

    print("=" * 80)
    print("ANÁLISIS COMPLETO DE TESTS POR CRITICIDAD - MeStore")
    print("=" * 80)

    total_tests = 0
    total_existentes = 0

    for categoria, datos in resultado.items():
        print(f"\n🔥 {categoria}")
        print(f"{'='*len(categoria)}")
        print(f"📊 Total: {datos['total']} | ✅ Existentes: {datos['existentes_count']} | ❌ No encontrados: {len(datos['no_existentes'])}")

        total_tests += datos['total']
        total_existentes += datos['existentes_count']

        if datos['existentes']:
            print("\n✅ TESTS EXISTENTES:")
            for i, test in enumerate(datos['existentes'], 1):
                print(f"   {i:2d}. {test}")

        if datos['no_existentes']:
            print(f"\n❌ TESTS NO ENCONTRADOS:")
            for test in datos['no_existentes']:
                print(f"   - {test}")

    print(f"\n" + "="*80)
    print(f"📈 RESUMEN TOTAL")
    print(f"{'='*80}")
    print(f"📊 Total de tests catalogados: {total_tests}")
    print(f"✅ Tests existentes: {total_existentes}")
    print(f"❌ Tests no encontrados: {total_tests - total_existentes}")
    print(f"📈 Porcentaje de cobertura: {(total_existentes/total_tests)*100:.1f}%")

    return resultado

if __name__ == "__main__":
    generar_reporte()