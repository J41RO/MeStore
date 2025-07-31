import re

# Leer el archivo actual
with open('app/api/v1/endpoints/vendedores.py', 'r') as f:
    content = f.read()

# Revertir a async
content = re.sub(r'^def registrar_vendedor\(', 'async def registrar_vendedor(', content, flags=re.MULTILINE)
content = re.sub(r'db: Session = Depends\(get_db\)', 'db: AsyncSession = Depends(get_db)', content)
content = re.sub(r'from sqlalchemy\.orm import Session', 'from sqlalchemy.ext.asyncio import AsyncSession', content)

# Agregar awaits que faltan
content = re.sub(r'result = db\.execute\(stmt\)', 'result = await db.execute(stmt)', content)
content = re.sub(r'db\.add\(new_user\)', 'db.add(new_user)', content)  # add() es sync siempre
content = re.sub(r'([^a]wait )db\.commit\(\)', r'\1await db.commit()', content)
content = re.sub(r'([^a]wait )db\.refresh\(', r'\1await db.refresh(', content)
content = re.sub(r'([^a]wait )db\.rollback\(\)', r'\1await db.rollback()', content)

# Escribir archivo corregido
with open('app/api/v1/endpoints/vendedores.py', 'w') as f:
    f.write(content)

print("✅ Endpoint revertido a async correctamente")
