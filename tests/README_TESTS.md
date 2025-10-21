# 🧪 Guía de Organización de Tests — MeStore

Este archivo define las **reglas oficiales** para mantener la carpeta `tests/` organizada y evitar el caos.

---

## 📁 Estructura Oficial

Cada test debe estar dentro de la carpeta correspondiente:

| Carpeta | Contiene | Ejemplos |
|----------|-----------|-----------|
| `api/` | Tests de endpoints, autenticación, vendedores, usuarios | `test_admin_orders_endpoints.py` |
| `models/` | Tests de modelos y ORM | `test_models_product.py` |
| `schemas/` | Validaciones Pydantic y estructuras de datos | `test_schemas_inventory.py` |
| `integration/` | Tests de integración con bases de datos o servicios externos | `test_transaction_status.py`, `test_wompi_service_methods.py` |
| `services/` | Tests de servicios internos (almacenamiento, reportes, etc.) | `test_storage_manager.py` |
| `fixtures/` | Datos preconfigurados, conftest y configuraciones especiales | `comprehensive_fixtures.py` |
| `unit/` | Plantillas o patrones TDD, pruebas unitarias puras | `tdd_framework.py`, `tdd_templates.py` |
| `scripts/` | Scripts de validación o automatización | `validate_all_endpoints.sh` |
| `misc/` | Archivos temporales o utilitarios no clasificables | `detailed_error_investigation.py` |
| `uncategorized/` | Tests nuevos sin categoría temporal (deben reclasificarse antes del commit) | — |

---

## ⚙️ Reglas de mantenimiento

1. **No dejar tests sueltos en la raíz (`tests/`)**  
   Todos los `test_*.py` deben estar dentro de una subcarpeta.

2. **Cada nuevo test debe indicar claramente su dominio**  
   Ejemplo: si prueba un endpoint → carpeta `api/`, si prueba un modelo → `models/`.

3. **Evitar duplicados o tests huérfanos.**  
   Si no estás seguro del destino, ubícalo temporalmente en `uncategorized/`  
   y notifica en el README o al equipo técnico.

4. **Respetar nombres consistentes:**  
test_<modulo>_<funcionalidad>.py

markdown
Copiar código
Ejemplo: `test_products_bulk_endpoints.py`

5. **No borrar ni mover fixtures sin verificar impacto en Pytest.**

6. **Usar los scripts de mantenimiento cuando se agreguen más de 5 tests nuevos.**
bash scripts/reorganize_tests.sh

yaml
Copiar código

---

## 🧩 Requerimientos técnicos mínimos

- **Python:** 3.11+
- **Framework de testing:** Pytest >= 7.4
- **Ejecución recomendada:**
```bash
pytest tests -q --disable-warnings
Recomendación: usar entorno virtual .venv activado.

🧠 Buenas prácticas adicionales
Documentar los tests complejos directamente en el encabezado del archivo.

Usar nombres expresivos y evitar abreviaturas confusas.

Validar con pytest --maxfail=2 antes de hacer commit.

🚀 Mantenimiento automatizado (opcional)
Para reorganizar automáticamente los tests si la estructura se rompe:

bash
Copiar código
bash scripts/reorganize_tests.sh
Este comando:

Reordena tests según su nombre.

Crea logs en logs/reorg_logs/.

No borra nada.

Última actualización: $(date +%F)
Autor: Jairo L. Colina M. — Smart Dev System / MeStore
