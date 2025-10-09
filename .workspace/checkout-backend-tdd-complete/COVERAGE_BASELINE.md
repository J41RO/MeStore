# COVERAGE BASELINE - Antes de TDD Completo

**Fecha**: 2025-10-09
**Análisis**: Pre-TDD estado actual de tests

---

## TESTS EXISTENTES ENCONTRADOS

### 1. Regression Tests
**Archivo**: `tests/regression/test_orders_stock_fix.py`

**Propósito**: Prevenir regresión del fix 5f263687 (Stock calculation async bug)

| Test | Línea | Descripción | Status |
|------|-------|-------------|--------|
| `test_order_creation_doesnt_return_500_with_stock_check` | 41 | Asegura que NO retorna 500 con stock check | ✅ EXISTE |
| `test_stock_calculation_bypass_works` | 114 | Valida bypass de get_stock_disponible() | ✅ EXISTE |
| `test_multiple_items_stock_validation` | 168 | Test con múltiples items | ✅ EXISTE |
| `test_no_relationship_method_calls_in_async_endpoint` | 237 | Code quality check (static) | ✅ EXISTE |

**Coverage**: Parcial - Solo cubre el async stock bug fix

### 2. Model Tests
**Archivo**: `tests/models/test_order.py`

Necesita revisión completa para determinar cobertura.

### 3. Service Tests
**Archivos**:
- `tests/services/test_order_state_service.py`
- `tests/services/test_order_tracking_service.py`
- `tests/services/test_notification_orders.py`

Coverage de servicios auxiliares, NO del endpoint principal.

---

## GAPS CRÍTICOS IDENTIFICADOS

### 🔴 PRIORITY 1: Security (NO COVERAGE)

| Gap | Severidad | Impacto |
|-----|-----------|---------|
| VENDOR validation (línea 96) | CRITICAL | Vendors pueden crear órdenes → 500 error |
| User authorization check | CRITICAL | User puede acceder órdenes de otros |
| JWT validation edge cases | HIGH | Token inválido/expirado |

### 🔴 PRIORITY 2: Core Logic (PARCIAL COVERAGE)

| Gap | Coverage | Impacto |
|-----|----------|---------|
| Stock calculation | ✅ Partial (regression only) | Solo async bug cubierto |
| Decimal precision | ❌ NONE | CHECK constraint violations |
| Total calculations | ❌ NONE | Tax, shipping, total |
| Order creation flow completo | ❌ NONE | E2E flow sin tests |

### 🟡 PRIORITY 3: Edge Cases (NO COVERAGE)

| Gap | Coverage | Impacto |
|-----|----------|---------|
| Empty cart validation | ❌ NONE | Business logic |
| Missing shipping info | ❌ NONE | Business logic |
| Invalid product_id format | ❌ NONE | Validation |
| Product without price | ❌ NONE | Business logic |
| Concurrent stock deduction | ❌ NONE | Race conditions |

### 🟢 PRIORITY 4: Features (NO COVERAGE)

| Feature | Coverage | Impacto |
|---------|----------|---------|
| Order tracking | ❌ NONE | Buyer experience |
| Order cancellation | ❌ NONE | Buyer experience |
| Order list/pagination | ❌ NONE | Buyer experience |
| Admin operations | ❌ NONE | Admin workflows |

---

## ESTIMATED CURRENT COVERAGE

```
app/api/v1/endpoints/orders.py:
- Stock calculation (async bypass): 80% ✅
- VENDOR validation: 0% ❌
- Authentication flow: 0% ❌
- Order creation flow: 20% ⚠️ (only happy path regression test)
- Total calculations: 0% ❌
- Tracking endpoint: 0% ❌
- Cancellation endpoint: 0% ❌

Overall: ~15-20% coverage (very low)
```

---

## CONCLUSIÓN FASE 1

**Estado Actual**: 
- ✅ Regression tests para 1 bug específico (stock async)
- ❌ NO hay comprehensive testing del checkout flow
- ❌ Security gaps críticos sin cubrir
- ❌ Business logic sin validación exhaustiva

**Necesidad TDD**: 
- RED Phase: Crear 40+ tests faltantes
- GREEN Phase: Implementar validaciones faltantes
- Coverage Target: >= 80%

**Próximo Paso**: FASE 2 - TDD RED Phase Setup

