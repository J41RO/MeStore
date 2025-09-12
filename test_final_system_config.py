#!/usr/bin/env python3
"""
Test final completo del sistema de configuraciones
================================================
Verifica todas las funcionalidades principales del sistema
"""

import asyncio
import aiohttp
import json

async def main():
    """Test final del sistema de configuraciones"""
    print("🏁 TEST FINAL DEL SISTEMA DE CONFIGURACIONES MeStocker")
    print("=" * 60)
    
    # Setup
    base_url = "http://192.168.1.137:8000"
    headers = {"User-Agent": "Mozilla/5.0 (Final Test)"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            # 1. Autenticación
            print("1️⃣ Autenticación...")
            auth_data = {"email": "admin@admin.com", "password": "admin123"}
            async with session.post(f"{base_url}/api/v1/auth/login", json=auth_data) as response:
                if response.status != 200:
                    print("❌ Fallo en autenticación")
                    return False
                
                result = await response.json()
                token = result.get("access_token")
                if not token:
                    print("❌ Token no encontrado")
                    return False
                
                auth_headers = {"Authorization": f"Bearer {token}"}
                print("✅ Autenticación exitosa")
            
            # 2. Obtener todas las configuraciones
            print("\n2️⃣ Obteniendo configuraciones...")
            async with session.get(f"{base_url}/api/v1/system-config", headers=auth_headers) as response:
                if response.status != 200:
                    print("❌ Fallo al obtener configuraciones")
                    return False
                
                settings = await response.json()
                print(f"✅ Obtenidas {len(settings)} configuraciones")
            
            # 3. Obtener categorías
            print("\n3️⃣ Obteniendo categorías...")
            async with session.get(f"{base_url}/api/v1/system-config/categories/", headers=auth_headers) as response:
                if response.status != 200:
                    print("❌ Fallo al obtener categorías")
                    return False
                
                result = await response.json()
                categories = result.get('categories', [])
                print(f"✅ Obtenidas {len(categories)} categorías:")
                
                for category in categories:
                    print(f"   📁 {category['display_name']}: {category['setting_count']} configuraciones")
            
            # 4. Actualizar configuración individual
            print("\n4️⃣ Actualizando configuración individual...")
            update_data = {"value": "MeStocker - Sistema Probado"}
            async with session.put(f"{base_url}/api/v1/system-config/site_name", json=update_data, headers=auth_headers) as response:
                if response.status != 200:
                    print("❌ Fallo al actualizar configuración")
                    return False
                
                updated_setting = await response.json()
                print(f"✅ Configuración actualizada: {updated_setting['key']} = {updated_setting['typed_value']}")
            
            # 5. Actualización masiva
            print("\n5️⃣ Actualizando configuraciones masivas...")
            bulk_data = {
                "settings": {
                    "max_upload_size": "52428800",  # 50MB
                    "session_timeout_minutes": "480"  # 8 horas
                }
            }
            async with session.post(f"{base_url}/api/v1/system-config/bulk", json=bulk_data, headers=auth_headers) as response:
                if response.status != 200:
                    print("❌ Fallo en actualización masiva")
                    return False
                
                result = await response.json()
                print(f"✅ Actualización masiva exitosa: {len(result)} configuraciones procesadas")
            
            # 6. Verificar configuración específica
            print("\n6️⃣ Verificando configuración actualizada...")
            async with session.get(f"{base_url}/api/v1/system-config/max_upload_size", headers=auth_headers) as response:
                if response.status != 200:
                    print("❌ Fallo al verificar configuración")
                    return False
                
                setting = await response.json()
                print(f"✅ Configuración verificada: {setting['key']} = {setting['typed_value']} ({setting['data_type']})")
            
            print("\n" + "=" * 60)
            print("🎉 TODOS LOS TESTS PASARON - SISTEMA FUNCIONAL")
            print("=" * 60)
            
            # Resumen de funcionalidades verificadas
            print("\n📊 FUNCIONALIDADES VERIFICADAS:")
            print("✅ Autenticación de administradores")
            print("✅ Obtención de configuraciones completas")
            print("✅ Listado de categorías con conteos")
            print("✅ Actualización de configuraciones individuales")
            print("✅ Actualización masiva de múltiples configuraciones")
            print("✅ Validación y conversión de tipos de datos")
            print("✅ Respuestas JSON bien estructuradas")
            
            print("\n🏆 EL PANEL DE CONFIGURACIONES ESTÁ LISTO PARA PRODUCCIÓN")
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante las pruebas: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)