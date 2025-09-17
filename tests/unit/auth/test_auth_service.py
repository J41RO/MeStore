#!/usr/bin/env python3
# test_auth_service.py - Test directo del AuthService
import asyncio
from app.services.auth_service import AuthService
from app.database import get_db

async def test_auth_service():
    """Test directo del AuthService.authenticate_user"""
    
    print("🧪 TESTING AuthService.authenticate_user...")
    print("=" * 50)
    
    auth_service = AuthService()
    
    # Obtener sesión de BD
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Crear engine síncrono para la sesión
    engine = create_engine('postgresql://mestocker_user:mestocker_pass@localhost/mestocker_dev')
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        # Test authenticate_user
        print("📊 Testing authenticate_user con admin@admin.com / admin123")
        
        try:
            user = await auth_service.authenticate_user(
                db=db,
                email="admin@admin.com", 
                password="admin123"
            )
            
            if user:
                print("🎉 AuthService.authenticate_user EXITOSO!")
                print(f"   Usuario: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Tipo: {user.user_type}")
                print(f"   Activo: {user.is_active}")
            else:
                print("❌ AuthService.authenticate_user retornó None")
                
                # Debug adicional
                print("\n🔍 Debug adicional:")
                from app.models.user import User
                user_check = db.query(User).filter(User.email == "admin@admin.com").first()
                
                if user_check:
                    print(f"✅ Usuario existe en BD: {user_check.email}")
                    
                    # Test manual de verify_password del AuthService
                    is_valid = await auth_service.verify_password("admin123", user_check.password_hash)
                    print(f"✅ AuthService.verify_password: {is_valid}")
                    
                    # Comparar con la función de utils
                    from app.utils.password import verify_password
                    is_valid_utils = await verify_password("admin123", user_check.password_hash)
                    print(f"✅ Utils.verify_password: {is_valid_utils}")
                else:
                    print("❌ Usuario no encontrado en BD")
                    
        except Exception as e:
            print(f"❌ Error en test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_service())