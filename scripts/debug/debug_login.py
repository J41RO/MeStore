#!/usr/bin/env python3
# debug_login.py - Debug del sistema de login
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.utils.password import hash_password, verify_password

async def debug_login():
    """Debug completo del sistema de login"""
    
    print("🔍 DEBUGGING LOGIN SYSTEM...")
    print("=" * 50)
    
    # Test 1: Verificar que el hash y verify funcionan
    print("📊 Test 1: Hash y Verify functionality")
    test_password = "admin123"
    
    try:
        # Generar hash
        hashed = await hash_password(test_password)
        print(f"✅ Hash generado: {hashed[:30]}...")
        
        # Verificar hash
        is_valid = await verify_password(test_password, hashed)
        print(f"✅ Verificación: {is_valid}")
        
        if not is_valid:
            print("❌ PROBLEMA: Hash y verify no funcionan juntos!")
            return
            
    except Exception as e:
        print(f"❌ Error en hash/verify: {e}")
        return
    
    # Test 2: Verificar usuario en BD
    print(f"\n📊 Test 2: Usuario en base de datos")
    engine = create_async_engine('postgresql+asyncpg://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    
    async with engine.begin() as conn:
        # Buscar usuario
        result = await conn.execute(
            text("SELECT email, password_hash, is_active, user_type FROM users WHERE email = :email"),
            {"email": "admin@admin.com"}
        )
        user = result.fetchone()
        
        if not user:
            print("❌ Usuario no encontrado en BD")
            return
            
        print(f"✅ Usuario encontrado:")
        print(f"   Email: {user[0]}")
        print(f"   Hash: {user[1][:30]}...")
        print(f"   Activo: {user[2]}")
        print(f"   Tipo: {user[3]}")
        
        # Test 3: Verificar password contra el de la BD
        print(f"\n📊 Test 3: Verificar password contra BD")
        db_hash = user[1]
        
        try:
            is_valid_db = await verify_password("admin123", db_hash)
            print(f"✅ Password contra BD: {is_valid_db}")
            
            if not is_valid_db:
                print("❌ PROBLEMA: Password no coincide con hash de BD")
                
                # Crear nuevo hash y actualizar
                print("🔧 Creando nuevo hash...")
                new_hash = await hash_password("admin123")
                
                await conn.execute(
                    text("UPDATE users SET password_hash = :hash WHERE email = :email"),
                    {"hash": new_hash, "email": "admin@admin.com"}
                )
                
                print("✅ Hash actualizado en BD")
                
                # Verificar nuevamente
                final_check = await verify_password("admin123", new_hash)
                print(f"✅ Verificación final: {final_check}")
                
        except Exception as e:
            print(f"❌ Error verificando password: {e}")
            
    await engine.dispose()
    
    # Test 4: Test de login directo via API
    print(f"\n📊 Test 4: Login via API")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://192.168.1.137:8000/api/v1/auth/login',
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
                },
                json={
                    'email': 'admin@admin.com',
                    'password': 'admin123'
                }
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    print("🎉 LOGIN API EXITOSO!")
                    print(f"   Token: {result.get('access_token', '')[:20]}...")
                else:
                    print(f"❌ Login API falló: {response.status}")
                    print(f"   Response: {result}")
                    
    except Exception as e:
        print(f"❌ Error en API test: {e}")

if __name__ == "__main__":
    asyncio.run(debug_login())