#!/usr/bin/env python3
"""
Script para poblar la base de datos con configuraciones predefinidas del sistema
===============================================================================
Este script inicializa la base de datos con las 19+ configuraciones predefinidas
organizadas por categorías según el instructivo de desarrollo.
"""

import asyncio
from app.database import AsyncSessionLocal
from app.models.system_setting import SystemSetting
from sqlalchemy.ext.asyncio import AsyncSession


async def populate_system_config():
    """Poblar la base de datos con configuraciones predefinidas"""
    async with AsyncSessionLocal() as session:
        try:
            print("🔧 Iniciando población de configuraciones del sistema...")
            
            # Verificar si ya existen configuraciones
            from sqlalchemy import select
            result = await session.execute(select(SystemSetting))
            existing_settings = result.scalars().all()
            
            if existing_settings:
                print(f"⚠️  Ya existen {len(existing_settings)} configuraciones en el sistema")
                response = input("¿Desea continuar y agregar las configuraciones faltantes? (y/N): ")
                if response.lower() not in ['y', 'yes', 'sí', 'si']:
                    print("❌ Cancelado por el usuario")
                    return
            
            # Obtener configuraciones predefinidas
            default_settings = SystemSetting.get_default_settings()
            
            # Contador de configuraciones agregadas
            added_count = 0
            updated_count = 0
            
            for setting_data in default_settings:
                # Verificar si ya existe la configuración
                result = await session.execute(
                    select(SystemSetting).where(SystemSetting.key == setting_data['key'])
                )
                existing_setting = result.scalar_one_or_none()
                
                if existing_setting:
                    print(f"⏭️  Configuración '{setting_data['key']}' ya existe, omitiendo...")
                    continue
                
                # Crear nueva configuración
                new_setting = SystemSetting(**setting_data)
                session.add(new_setting)
                
                print(f"✅ Agregando: {setting_data['key']} ({setting_data['category']})")
                added_count += 1
            
            # Confirmar cambios
            await session.commit()
            
            print(f"\n🎉 Proceso completado exitosamente!")
            print(f"📊 Resumen:")
            print(f"   • Configuraciones agregadas: {added_count}")
            print(f"   • Total configuraciones disponibles: {len(default_settings)}")
            
            # Mostrar resumen por categorías
            print(f"\n📋 Configuraciones por categoría:")
            categories = {}
            for setting in default_settings:
                category = setting['category']
                categories[category] = categories.get(category, 0) + 1
            
            category_names = {
                'general': 'General',
                'email': 'Email',
                'business': 'Negocio', 
                'security': 'Seguridad'
            }
            
            for category, count in categories.items():
                name = category_names.get(category, category.title())
                print(f"   • {name}: {count} configuraciones")
                
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante la población: {e}")
            raise


async def verify_population():
    """Verificar que las configuraciones se poblaron correctamente"""
    async with AsyncSessionLocal() as session:
        try:
            print("\n🔍 Verificando población de configuraciones...")
            
            from sqlalchemy import select, func
            
            # Contar total de configuraciones
            result = await session.execute(
                select(func.count(SystemSetting.id))
            )
            total_count = result.scalar()
            
            # Contar por categoría
            result = await session.execute(
                select(SystemSetting.category, func.count(SystemSetting.id))
                .group_by(SystemSetting.category)
            )
            category_counts = result.all()
            
            # Contar editables vs solo lectura
            result = await session.execute(
                select(func.count(SystemSetting.id))
                .where(SystemSetting.is_editable == True)
            )
            editable_count = result.scalar()
            
            result = await session.execute(
                select(func.count(SystemSetting.id))
                .where(SystemSetting.is_public == True)
            )
            public_count = result.scalar()
            
            print(f"📊 Estadísticas de configuraciones:")
            print(f"   • Total configuraciones: {total_count}")
            print(f"   • Configuraciones editables: {editable_count}")
            print(f"   • Configuraciones públicas: {public_count}")
            print(f"   • Solo lectura: {total_count - editable_count}")
            
            print(f"\n📋 Por categoría:")
            category_names = {
                'general': 'General',
                'email': 'Email',
                'business': 'Negocio',
                'security': 'Seguridad'
            }
            
            for category, count in category_counts:
                name = category_names.get(category, category.title())
                print(f"   • {name}: {count} configuraciones")
            
            # Mostrar algunas configuraciones de ejemplo
            print(f"\n🔍 Ejemplos de configuraciones:")
            result = await session.execute(
                select(SystemSetting.key, SystemSetting.category, SystemSetting.description)
                .limit(5)
            )
            
            for key, category, description in result:
                print(f"   • {key} ({category}): {description[:50]}...")
                
        except Exception as e:
            print(f"❌ Error durante la verificación: {e}")


async def main():
    """Función principal"""
    try:
        await populate_system_config()
        await verify_population()
        print(f"\n✅ Sistema de configuraciones poblado exitosamente!")
        print(f"🚀 El panel de configuraciones está listo para usar")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)