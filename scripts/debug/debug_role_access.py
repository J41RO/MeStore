#!/usr/bin/env python3
"""
Script para debuggear el acceso de roles desde el backend
"""

import json

import requests


def debug_user_role_data():
    """Verificar exactamente qué datos está devolviendo el backend"""

    print("🕵️‍♂️ ANÁLISIS FORENSE - DATOS DE USUARIO DESDE BACKEND")
    print("=" * 60)

    # Testear con vendor
    email = "vendor@mestore.com"
    password = "123456"

    print(f"🔐 Probando con: {email}")

    try:
        # Login
        login_response = requests.post(
            "http://192.168.1.137:8000/api/v1/auth/login",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0",
            },
            json={"email": email, "password": password},
            timeout=10,
        )

        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.status_code}")
            return

        token = login_response.json()["access_token"]
        print(f"✅ Login exitoso")

        # Obtener datos del usuario
        user_response = requests.get(
            "http://192.168.1.137:8000/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0",
            },
            timeout=10,
        )

        if user_response.status_code != 200:
            print(f"❌ Error obteniendo usuario: {user_response.status_code}")
            return

        user_data = user_response.json()

        print(f"\n📊 DATOS RAW DEL BACKEND:")
        print(json.dumps(user_data, indent=2))

        print(f"\n🔍 ANÁLISIS ESPECÍFICO:")
        print(f"   email: '{user_data.get('email')}'")
        print(f"   user_type: '{user_data.get('user_type')}'")
        print(f"   tipo de user_type: {type(user_data.get('user_type'))}")
        print(f"   longitud de user_type: {len(user_data.get('user_type', ''))}")

        # Verificar caracteres especiales
        user_type = user_data.get("user_type", "")
        print(f"   bytes de user_type: {user_type.encode('utf-8')}")
        print(f"   repr de user_type: {repr(user_type)}")

        # Simular lo que haría el frontend
        print(f"\n🖥️ SIMULACIÓN FRONTEND:")

        # Enum esperado en TypeScript
        typescript_enum = {
            "COMPRADOR": "COMPRADOR",
            "VENDEDOR": "VENDEDOR",
            "ADMIN": "ADMIN",
            "SUPERUSER": "SUPERUSER",
        }

        # Hierarchy como está definido en el frontend
        role_hierarchy = {"COMPRADOR": 1, "VENDEDOR": 2, "ADMIN": 3, "SUPERUSER": 4}

        print(f"   ¿user_type está en typescript_enum? {user_type in typescript_enum}")
        print(f"   ¿user_type está en role_hierarchy? {user_type in role_hierarchy}")
        print(
            f"   Valor en role_hierarchy: {role_hierarchy.get(user_type, 'NO ENCONTRADO')}"
        )

        # Test de validación específica para vendor-dashboard
        print(f"\n🛣️ TEST PARA /app/vendor-dashboard:")
        required_role = "VENDEDOR"
        user_level = role_hierarchy.get(user_type, 0)
        required_level = role_hierarchy.get(required_role, 999)

        print(f"   Usuario tiene rol: '{user_type}' (nivel {user_level})")
        print(f"   Se requiere rol: '{required_role}' (nivel {required_level})")
        print(
            f"   ¿Acceso permitido? {'✅ SÍ' if user_level >= required_level else '❌ NO'}"
        )

        # Test de comparación exacta
        print(f"\n🎯 TEST DE COMPARACIÓN EXACTA:")
        print(f"   user_type == 'VENDEDOR': {user_type == 'VENDEDOR'}")
        print(
            f"   user_type === 'VENDEDOR' (JS equivalent): {user_type is not None and str(user_type) == 'VENDEDOR'}"
        )

        # Verificar espacios o caracteres ocultos
        if user_type != user_type.strip():
            print(
                f"   ⚠️ PROBLEMA: user_type tiene espacios! '{user_type}' vs '{user_type.strip()}'"
            )

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    debug_user_role_data()
