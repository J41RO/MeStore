#!/usr/bin/env python3
"""
Script de debug para probar autenticación y obtener datos del usuario
"""

import json

import requests

BASE_URL = "http://192.168.1.137:8000/api/v1"


def test_auth_and_get_user_data(email, password, expected_role):
    """Probar login y obtener datos completos del usuario"""
    print(f"\n🔍 DEBUG - Probando: {email}")

    # Usar endpoint específico para admin/superuser
    endpoint = (
        "/auth/admin-login"
        if expected_role in ["ADMIN", "SUPERUSER"]
        else "/auth/login"
    )

    try:
        # Paso 1: Login
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0",
            },
            json={"email": email, "password": password},
            timeout=10,
        )

        if response.status_code != 200:
            print(f"❌ Login fallido: {response.status_code}")
            return None

        data = response.json()
        token = data.get("access_token")

        if not token:
            print("❌ No se obtuvo token")
            return None

        print(f"✅ Login exitoso, token: {token[:20]}...")

        # Paso 2: Obtener información del usuario usando /me
        me_response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "MeStore-Frontend/1.0",
            },
            timeout=10,
        )

        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"📊 Datos completos del usuario:")
            print(json.dumps(user_data, indent=2))
            return {"token": token, "user_data": user_data}
        else:
            print(f"❌ Error obteniendo info de usuario: {me_response.status_code}")
            try:
                error_data = me_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Error: {me_response.text}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Probar todos los usuarios y mostrar datos completos"""
    print("=== DEBUG AUTENTICACIÓN ===")

    test_users = [
        ("buyer@mestore.com", "123456", "COMPRADOR"),
        ("vendor@mestore.com", "123456", "VENDEDOR"),
        ("admin@mestore.com", "123456", "ADMIN"),
        ("super@mestore.com", "123456", "SUPERUSER"),
    ]

    for email, password, expected_role in test_users:
        result = test_auth_and_get_user_data(email, password, expected_role)
        if result:
            print(f"✅ {email} autenticado correctamente")
        else:
            print(f"❌ {email} falló la autenticación")
        print("-" * 50)


if __name__ == "__main__":
    main()
