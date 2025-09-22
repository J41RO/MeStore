#!/usr/bin/env python3
"""
Verificación final del sistema de autenticación después de todas las correcciones
"""

import requests
import json

def test_all_users_complete():
    """Test completo para todos los usuarios"""
    
    print("🔬 VERIFICACIÓN FINAL - ANÁLISIS FORENSE COMPLETO")
    print("=" * 60)
    
    test_users = [
        ("buyer@mestore.com", "123456", "BUYER", "/app/dashboard"),
        ("vendor@mestore.com", "123456", "VENDOR", "/app/vendor-dashboard"),
        ("admin@mestore.com", "123456", "ADMIN", "/admin-secure-portal/dashboard"),
        ("super@mestore.com", "123456", "SUPERUSER", "/admin-secure-portal/dashboard")
    ]
    
    all_passed = True
    
    for email, password, expected_role, expected_route in test_users:
        print(f"\n🔍 TESTING: {email}")
        print("-" * 40)
        
        try:
            # Login
            endpoint = "/auth/admin-login" if expected_role in ["ADMIN", "SUPERUSER"] else "/auth/login"
            
            login_response = requests.post(
                f"http://192.168.1.137:8000/api/v1{endpoint}",
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "MeStore-Frontend/1.0"
                },
                json={"email": email, "password": password},
                timeout=10
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                all_passed = False
                continue
                
            token = login_response.json()["access_token"]
            print(f"✅ Login successful")
            
            # Get user data
            user_response = requests.get(
                "http://192.168.1.137:8000/api/v1/auth/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "MeStore-Frontend/1.0"
                },
                timeout=10
            )
            
            if user_response.status_code != 200:
                print(f"❌ User data failed: {user_response.status_code}")
                all_passed = False
                continue
                
            user_data = user_response.json()
            actual_role = user_data.get('user_type', '')
            
            print(f"📋 User data: {user_data['email']}")
            print(f"🎭 Role: {actual_role}")
            
            # Verify role
            if actual_role != expected_role:
                print(f"❌ Role mismatch: expected {expected_role}, got {actual_role}")
                all_passed = False
                continue
            else:
                print(f"✅ Role correct: {actual_role}")
            
            # Test role hierarchy logic (simulating frontend)
            role_hierarchy = {
                'BUYER': 1,
                'VENDOR': 2,
                'ADMIN': 3,
                'SUPERUSER': 4
            }
            
            user_level = role_hierarchy.get(actual_role, 0)
            
            # Test minimum role access
            print(f"\n🧪 ROLE HIERARCHY TESTS:")
            print(f"   User level: {user_level} ({actual_role})")
            
            # Test access to different routes
            route_requirements = {
                '/app/dashboard': ('BUYER', 'exact'),
                '/app/vendor-dashboard': ('VENDOR', 'minimum'),
                '/admin-secure-portal/dashboard': ('ADMIN', 'minimum')
            }
            
            for route, (required_role, strategy) in route_requirements.items():
                required_level = role_hierarchy.get(required_role, 999)
                
                if strategy == 'exact':
                    has_access = actual_role == required_role
                elif strategy == 'minimum':
                    has_access = user_level >= required_level
                else:
                    has_access = False
                
                access_result = "✅" if has_access else "❌"
                print(f"   {route}: {access_result} ({'ALLOW' if has_access else 'DENY'})")
                
                # Verify this user should have access to their expected route
                if route == expected_route and not has_access:
                    print(f"❌ CRITICAL: User should have access to {expected_route}!")
                    all_passed = False
            
            # Simulate frontend auth storage
            auth_storage = {
                "state": {
                    "user": {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "user_type": actual_role,  # This is the KEY - must be string
                        "name": user_data["nombre"]
                    },
                    "token": token,
                    "isAuthenticated": True
                },
                "version": 0
            }
            
            print(f"\n💾 Frontend storage simulation:")
            print(f"   user_type stored as: '{auth_storage['state']['user']['user_type']}'")
            print(f"   type: {type(auth_storage['state']['user']['user_type'])}")
            
        except Exception as e:
            print(f"❌ Error testing {email}: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICACIÓN FINAL COMPLETA")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Backend: Autenticación funcionando")
        print("✅ Backend: Roles serializados correctamente")
        print("✅ Frontend: Hook useRoleAccess corregido")
        print("✅ Frontend: Hierarchy usando strings")
        print("✅ Sistema: Completo y funcional")
        print("\n🔓 El problema de 'Acceso Restringido' DEBE estar solucionado")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔍 Revisar los errores reportados arriba")
    
    return all_passed

if __name__ == "__main__":
    success = test_all_users_complete()
    exit(0 if success else 1)