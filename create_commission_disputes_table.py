#!/usr/bin/env python3
"""
Script para crear tabla commission_disputes manualmente usando FastAPI setup.
"""

import asyncio
from sqlalchemy import text
from app.database import get_db_session
from app.models.commission_dispute import ComissionDispute
from app.models.base import Base
from app.database import engine

async def create_commission_disputes_table():
    """Crear tabla commission_disputes y sus índices"""
    
    print("🔗 Conectando a base de datos...")
    
    try:
        # Usar la conexión que ya funciona en FastAPI
        async with engine.begin() as conn:
            print("✅ Conexión establecida")
            
            # Verificar si tabla ya existe
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'commission_disputes'
                );
            """))
            
            table_exists = result.scalar()
            
            if table_exists:
                print("ℹ️ TABLA commission_disputes YA EXISTE")
                
                # Verificar estructura
                columns_result = await conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'commission_disputes'
                    ORDER BY ordinal_position;
                """))
                
                columns = columns_result.fetchall()
                print("📋 ESTRUCTURA ACTUAL:")
                for col in columns:
                    print(f"   • {col[0]}: {col[1]}")
                
                return True
            
            print("🗃️ CREANDO TABLA commission_disputes...")
            
            # Crear tabla usando SQL directo
            await conn.execute(text("""
                CREATE TABLE commission_disputes (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    transaction_id UUID NOT NULL,
                    usuario_id UUID NOT NULL,
                    motivo VARCHAR(100) NOT NULL,
                    descripcion TEXT NOT NULL,
                    estado VARCHAR(20) DEFAULT 'ABIERTO' NOT NULL,
                    respuesta_admin TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMPTZ,
                    
                    CONSTRAINT fk_dispute_transaction 
                        FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                    CONSTRAINT fk_dispute_usuario 
                        FOREIGN KEY (usuario_id) REFERENCES users(id)
                );
            """))
            
            print("📊 CREANDO ÍNDICES...")
            
            # Crear índices
            await conn.execute(text("""
                CREATE INDEX ix_dispute_transaction_estado 
                ON commission_disputes(transaction_id, estado);
            """))
            
            await conn.execute(text("""
                CREATE INDEX ix_dispute_usuario_estado 
                ON commission_disputes(usuario_id, estado);
            """))
            
            await conn.execute(text("""
                CREATE INDEX ix_dispute_fecha_estado 
                ON commission_disputes(created_at, estado);
            """))
            
            # Crear índices básicos para foreign keys
            await conn.execute(text("""
                CREATE INDEX ix_commission_disputes_transaction_id 
                ON commission_disputes(transaction_id);
            """))
            
            await conn.execute(text("""
                CREATE INDEX ix_commission_disputes_usuario_id 
                ON commission_disputes(usuario_id);
            """))
            
            await conn.execute(text("""
                CREATE INDEX ix_commission_disputes_estado 
                ON commission_disputes(estado);
            """))
            
            print("✅ TABLA E ÍNDICES CREADOS EXITOSAMENTE")
            
            # Verificar creación
            verify_result = await conn.execute(text("""
                SELECT COUNT(*) as column_count
                FROM information_schema.columns 
                WHERE table_name = 'commission_disputes';
            """))
            
            column_count = verify_result.scalar()
            print(f"📊 TABLA CREADA CON {column_count} COLUMNAS")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_commission_disputes_table())
    if success:
        print("🎉 ✅ TABLA COMMISSION_DISPUTES LISTA PARA USO")
    else:
        print("❌ FALLO EN CREACIÓN DE TABLA")
