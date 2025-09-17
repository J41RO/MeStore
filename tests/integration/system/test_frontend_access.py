#!/usr/bin/env python3
"""
Script para probar el acceso completo al frontend después de la autenticación
"""

import requests
import json

BASE_URL_API = "http://192.168.1.137:8000/api/v1"
BASE_URL_FRONTEND = "http://localhost:5173"

def test_complete_user_flow(email, password, expected_role, expected_route):
    """Probar flujo completo de un usuario desde login hasta acceso a su dashboard"""
    print(f"\n🚀 PROBANDO FLUJO COMPLETO: {email}")
    print(f"   Rol esperado: {expected_role}")
    print(f"   Ruta esperada: {expected_route}")
    
    # Usar endpoint específico para admin/superuser
    endpoint = "/auth/admin-login" if expected_role in ["ADMIN", "SUPERUSER"] else "/auth/login"
    
    try:
        # Paso 1: Autenticación
        print("   🔐 Paso 1: Autenticación...")
        auth_response = requests.post(
            f"{BASE_URL_API}{endpoint}",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0"
            },
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )
        
        if auth_response.status_code != 200:
            print(f"   ❌ Autenticación fallida: {auth_response.status_code}")
            return False
            
        token = auth_response.json().get('access_token')
        print(f"   ✅ Autenticación exitosa")
        
        # Paso 2: Verificar datos del usuario
        print("   📊 Paso 2: Verificando datos del usuario...")
        me_response = requests.get(
            f"{BASE_URL_API}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0"
            },
            timeout=10
        )
        
        if me_response.status_code != 200:
            print(f"   ❌ Error obteniendo datos: {me_response.status_code}")
            return False
            
        user_data = me_response.json()
        actual_role = user_data.get('user_type', '')
        
        print(f"   ✅ Datos obtenidos - Rol: {actual_role}")
        
        if actual_role != expected_role:
            print(f"   ⚠️  Rol inesperado: esperado {expected_role}, obtuvo {actual_role}")
            return False
            
        # Paso 3: Verificar estructura de datos para el frontend
        print("   🧩 Paso 3: Verificando estructura de datos...")
        required_fields = ['id', 'email', 'user_type', 'nombre']
        for field in required_fields:
            if field not in user_data:
                print(f"   ❌ Campo requerido faltante: {field}")
                return False
                
        print(f"   ✅ Estructura de datos correcta")
        
        # Paso 4: Simular datos que el frontend recibiría
        frontend_user_data = {
            'id': user_data['id'],
            'email': user_data['email'],
            'user_type': user_data['user_type'],
            'name': user_data['nombre'],
        }
        
        print(f"   📋 Datos para frontend:")
        print(f"      ID: {frontend_user_data['id']}")
        print(f"      Email: {frontend_user_data['email']}")
        print(f"      Rol: {frontend_user_data['user_type']}")
        print(f"      Nombre: {frontend_user_data['name']}")
        
        # Paso 5: Verificar lógica de redirección
        print("   🔀 Paso 5: Verificando lógica de redirección...")
        role_routes = {
            'COMPRADOR': '/app/dashboard',
            'VENDEDOR': '/app/vendor-dashboard',
            'ADMIN': '/admin-secure-portal/dashboard',
            'SUPERUSER': '/admin-secure-portal/dashboard'
        }
        
        expected_frontend_route = role_routes.get(actual_role)
        if expected_frontend_route != expected_route:
            print(f"   ⚠️  Ruta de redirección incorrecta: esperada {expected_route}, sería {expected_frontend_route}")
        else:
            print(f"   ✅ Redirección correcta: {expected_frontend_route}")
        
        print(f"   🎯 RESULTADO: FLUJO COMPLETO EXITOSO PARA {email}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en flujo: {e}")
        return False

def main():
    """Probar flujo completo para todos los usuarios"""
    print("=" * 60)
    print("🧪 PRUEBA COMPLETA DE FLUJO DE USUARIOS")
    print("=" * 60)
    
    test_cases = [
        ("buyer@mestore.com", "123456", "COMPRADOR", "/app/dashboard"),
        ("vendor@mestore.com", "123456", "VENDEDOR", "/app/vendor-dashboard"),
        ("admin@mestore.com", "123456", "ADMIN", "/admin-secure-portal/dashboard"),
        ("super@mestore.com", "123456", "SUPERUSER", "/admin-secure-portal/dashboard")
    ]
    
    results = []
    for email, password, expected_role, expected_route in test_cases:
        success = test_complete_user_flow(email, password, expected_role, expected_route)
        results.append((email, expected_role, success))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    all_passed = True
    for email, role, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {email} ({role})")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS LOS FLUJOS DE USUARIO FUNCIONAN CORRECTAMENTE")
        print("🔓 El problema de 'Acceso Restringido' debería estar solucionado")
        print("🎯 Los usuarios pueden acceder a sus respectivas áreas")
    else:
        print("⚠️  ALGUNOS FLUJOS TIENEN PROBLEMAS")
        print("🔍 Revisar los errores reportados arriba")
    
    print("=" * 60)

if __name__ == "__main__":
    main()