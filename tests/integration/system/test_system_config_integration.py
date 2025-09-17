#!/usr/bin/env python3
"""
Script de testing integral del sistema de configuraciones
========================================================
Prueba todos los endpoints, validaciones y funcionalidades del sistema
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


class SystemConfigTester:
    """Tester integral del sistema de configuraciones"""
    
    def __init__(self, base_url: str = "http://192.168.1.137:8000"):
        self.base_url = base_url
        self.auth_headers = {}
        self.session = None
    
    async def setup_session(self):
        """Configurar sesión HTTP"""
        headers = {"User-Agent": "Mozilla/5.0 (SystemConfig Tester)"}
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def cleanup_session(self):
        """Limpiar sesión HTTP"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self, username: str = "admin@admin.com", password: str = "admin123"):
        """Autenticarse para obtener token de acceso"""
        try:
            print("🔐 Autenticando usuario...")
            
            auth_data = {
                "email": username,
                "password": password
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    access_token = result.get("access_token")
                    
                    if access_token:
                        self.auth_headers = {"Authorization": f"Bearer {access_token}"}
                        print("✅ Autenticación exitosa")
                        return True
                    
                print(f"❌ Error en autenticación: Token no encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            return False
    
    async def test_get_all_settings(self) -> bool:
        """Test: Obtener todas las configuraciones"""
        try:
            print("\n📋 Probando: GET /api/v1/system-config")
            
            async with self.session.get(
                f"{self.base_url}/api/v1/system-config",
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    settings = await response.json()
                    print(f"✅ Obtenidas {len(settings)} configuraciones")
                    
                    # Verificar estructura
                    if settings:
                        first_setting = settings[0]
                        required_fields = ['id', 'key', 'value', 'category', 'data_type', 'description']
                        
                        for field in required_fields:
                            if field not in first_setting:
                                print(f"❌ Campo faltante: {field}")
                                return False
                        
                        print(f"📄 Ejemplo: {first_setting['key']} = {first_setting.get('typed_value')}")
                        return True
                    
                print(f"❌ No se encontraron configuraciones")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_get_categories(self) -> bool:
        """Test: Obtener categorías"""
        try:
            print("\n📂 Probando: GET /api/v1/system-config/categories/")
            
            async with self.session.get(
                f"{self.base_url}/api/v1/system-config/categories/",
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    categories = result.get('categories', [])
                    
                    print(f"✅ Obtenidas {len(categories)} categorías")
                    
                    expected_categories = ['general', 'email', 'business', 'security']
                    for category in categories:
                        print(f"📁 {category['display_name']}: {category['setting_count']} configuraciones")
                    
                    return len(categories) >= 4
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_get_single_setting(self, key: str = "site_name") -> bool:
        """Test: Obtener una configuración específica"""
        try:
            print(f"\n🔍 Probando: GET /api/v1/system-config/{key}")
            
            async with self.session.get(
                f"{self.base_url}/api/v1/system-config/{key}",
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    setting = await response.json()
                    print(f"✅ Configuración obtenida: {setting['key']} = {setting.get('typed_value')}")
                    return True
                    
                print(f"❌ Error {response.status}: {await response.text()}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_update_setting(self, key: str = "site_name", test_value: str = "MeStocker Test") -> bool:
        """Test: Actualizar una configuración"""
        try:
            print(f"\n✏️ Probando: PUT /api/v1/system-config/{key}")
            
            update_data = {"value": test_value}
            
            async with self.session.put(
                f"{self.base_url}/api/v1/system-config/{key}",
                json=update_data,
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    updated_setting = await response.json()
                    print(f"✅ Configuración actualizada: {updated_setting['key']} = {updated_setting.get('typed_value')}")
                    return True
                    
                print(f"❌ Error {response.status}: {await response.text()}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_bulk_update(self) -> bool:
        """Test: Actualización masiva"""
        try:
            print(f"\n🔄 Probando: POST /api/v1/system-config/bulk")
            
            bulk_data = {
                "settings": {
                    "maintenance_mode": "false",
                    "max_upload_size": "20971520"  # 20MB
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/system-config/bulk",
                json=bulk_data,
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Actualización masiva exitosa: {result.get('updated_count', 0)} configuraciones actualizadas")
                    return True
                    
                print(f"❌ Error {response.status}: {await response.text()}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def test_validation(self) -> bool:
        """Test: Validación de tipos de datos"""
        try:
            print(f"\n✅ Probando: Validación de tipos de datos")
            
            # Test 1: Boolean inválido
            invalid_bool = {"value": "invalid_boolean"}
            
            async with self.session.put(
                f"{self.base_url}/api/v1/system-config/maintenance_mode",
                json=invalid_bool,
                headers=self.auth_headers
            ) as response:
                if response.status != 422:  # Debería fallar la validación
                    print(f"❌ La validación no funcionó correctamente")
                    return False
            
            # Test 2: Integer válido
            valid_int = {"value": "300"}  # 5 minutos
            
            async with self.session.put(
                f"{self.base_url}/api/v1/system-config/session_timeout_minutes",
                json=valid_int,
                headers=self.auth_headers
            ) as response:
                if response.status == 200:
                    print("✅ Validación de tipos funcionando correctamente")
                    return True
                    
            return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Ejecutar todos los tests"""
        results = {}
        
        print("🚀 Iniciando tests del sistema de configuraciones")
        print("=" * 60)
        
        await self.setup_session()
        
        try:
            # Autenticación
            if not await self.authenticate():
                print("❌ Falló la autenticación, cancelando tests")
                return {"authentication": False}
            
            # Tests de funcionalidad
            results["get_all_settings"] = await self.test_get_all_settings()
            results["get_categories"] = await self.test_get_categories()
            results["get_single_setting"] = await self.test_get_single_setting()
            results["update_setting"] = await self.test_update_setting()
            results["bulk_update"] = await self.test_bulk_update()
            results["validation"] = await self.test_validation()
            
        finally:
            await self.cleanup_session()
        
        return results
    
    def print_results(self, results: Dict[str, bool]):
        """Imprimir resumen de resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE TESTS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Resultado final: {passed}/{total} tests pasaron")
        
        if passed == total:
            print("🎉 ¡Todos los tests pasaron! El sistema está funcionando correctamente")
        else:
            print("⚠️  Algunos tests fallaron, revisar la configuración")


async def main():
    """Función principal"""
    tester = SystemConfigTester()
    results = await tester.run_all_tests()
    tester.print_results(results)
    
    # Verificar resultado final
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    print("🧪 Sistema de Testing de Configuraciones MeStocker")
    print("=" * 60)
    
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏸️  Tests interrumpidos por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        exit(1)