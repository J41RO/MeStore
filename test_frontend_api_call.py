#!/usr/bin/env python3
"""
Script para simular las llamadas del frontend al backend.
Este script ayuda a debuggear problemas de autenticación y endpoints.
"""

import requests
import json
import sys

def test_admin_auth():
    """Probar autenticación como admin"""
    
    print("🔑 PROBANDO AUTENTICACIÓN DE ADMIN")
    print("=" * 40)
    
    # URL base del backend 
    base_url = "http://192.168.1.137:8000"
    
    # Credenciales de admin (usando el admin que creamos antes)
    admin_credentials = {
        "email": "admin@mestore.com",
        "password": "admin123"
    }
    
    try:
        # 1. Intentar login
        print("1️⃣  Intentando login...")
        
        login_url = f"{base_url}/api/v1/auth/login"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible frontend test)"
        }
        
        response = requests.post(
            login_url, 
            json=admin_credentials,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access_token')
            print(f"   ✅ Login exitoso")
            print(f"   🔑 Token obtenido: {access_token[:50]}...")
            return access_token
        else:
            print(f"   ❌ Login fallido: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error en login: {str(e)}")
        return None

def test_incoming_products_api(access_token):
    """Probar endpoint de incoming products"""
    
    print("\n📦 PROBANDO ENDPOINT INCOMING PRODUCTS")
    print("=" * 45)
    
    base_url = "http://192.168.1.137:8000"
    endpoint_url = f"{base_url}/api/v1/inventory/queue/incoming-products"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible frontend test)"
    }
    
    try:
        print(f"1️⃣  Llamando endpoint: {endpoint_url}")
        
        response = requests.get(
            endpoint_url,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa")
            print(f"   📊 Productos encontrados: {len(data)}")
            
            # Mostrar resumen de los productos
            for i, product in enumerate(data[:3]):  # Solo primeros 3
                print(f"   🔸 {i+1}. {product.get('tracking_number')} - {product.get('verification_status')}")
            
            return True
        else:
            print(f"   ❌ Error en endpoint: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en llamada: {str(e)}")
        return False

def test_stats_api(access_token):
    """Probar endpoint de estadísticas"""
    
    print("\n📊 PROBANDO ENDPOINT DE ESTADÍSTICAS")
    print("=" * 40)
    
    base_url = "http://192.168.1.137:8000"
    endpoint_url = f"{base_url}/api/v1/inventory/queue/stats"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible frontend test)"
    }
    
    try:
        print(f"1️⃣  Llamando endpoint: {endpoint_url}")
        
        response = requests.get(
            endpoint_url,
            headers=headers,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Respuesta exitosa")
            print(f"   📊 Stats: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   ❌ Error en endpoint: {response.status_code}")
            print(f"   📄 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en llamada: {str(e)}")
        return False

def main():
    """Función principal"""
    
    print("🧪 TESTING FRONTEND-BACKEND COMMUNICATION")
    print("=" * 50)
    
    # 1. Probar autenticación
    access_token = test_admin_auth()
    if not access_token:
        print("\n❌ NO SE PUDO AUTENTICAR - Abortando tests")
        return False
    
    # 2. Probar endpoint de productos
    products_ok = test_incoming_products_api(access_token)
    
    # 3. Probar endpoint de estadísticas  
    stats_ok = test_stats_api(access_token)
    
    # Resumen
    print("\n🎯 RESUMEN DE TESTS:")
    print("=" * 25)
    print(f"Autenticación:     {'✅ OK' if access_token else '❌ ERROR'}")
    print(f"Endpoint productos: {'✅ OK' if products_ok else '❌ ERROR'}")
    print(f"Endpoint stats:     {'✅ OK' if stats_ok else '❌ ERROR'}")
    
    if access_token and products_ok:
        print("\n✅ BACKEND FUNCIONANDO CORRECTAMENTE")
        print("🔍 El problema debe estar en el frontend:")
        print("   - Verificar token storage en localStorage")
        print("   - Verificar network tab en DevTools")
        print("   - Verificar console errors en browser")
        return True
    else:
        print("\n❌ HAY PROBLEMAS EN EL BACKEND")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)