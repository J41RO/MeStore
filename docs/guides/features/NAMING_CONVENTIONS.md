# NAMING CONVENTIONS - MeStore Enterprise

## Purpose

This document establishes consistent naming conventions for all files, directories, and documentation across the MeStore project. Consistent naming improves discoverability, maintainability, and professionalism.

---

## General Principles

### 1. Clarity Over Brevity
- Use descriptive names that clearly indicate content
- Avoid cryptic abbreviations
- Full words preferred over acronyms (unless widely recognized)

### 2. Consistency Across Project
- Same naming pattern for similar file types
- Predictable structure makes finding files easier
- Follow established patterns when adding new files

### 3. Machine and Human Readable
- Use characters that work across all operating systems
- Avoid spaces (use underscores or hyphens)
- Use consistent case conventions

### 4. Hierarchical Organization
- Most important information first in filename
- Use prefixes to group related files
- Date suffixes for time-based organization

---

## File Naming Conventions

### Documentation Files (.md)

#### Format: `{CATEGORY}_{DESCRIPTION}_{TYPE}.md`

**Components**:
- `CATEGORY`: High-level category (TDD, E2E, API, MVP, etc.)
- `DESCRIPTION`: Specific topic or feature (clear, concise)
- `TYPE`: Document type (REPORT, SUMMARY, GUIDE, ANALYSIS, etc.)

**Case Style**: SCREAMING_SNAKE_CASE (ALL CAPS with underscores)

**Examples**:
```
✓ TDD_SECURITY_ANALYSIS_REPORT.md
✓ E2E_TESTING_COMPLETE_SUMMARY.md
✓ API_ARCHITECTURE_DIAGRAM.md
✓ MVP_EXECUTIVE_SUMMARY.md
✓ PAYMENT_INTEGRATION_COMPLETE_GUIDE.md
✓ DATABASE_SETUP.md

✗ tdd-report.md                    (Too vague, wrong case)
✗ Testing Summary.md               (Spaces, unclear category)
✗ payment_stuff.md                 (Unprofessional, no category)
✗ report_final_v3_FINAL.md         (Version numbers belong in git)
```

#### Document Type Suffixes

| Suffix | Purpose | Example |
|--------|---------|---------|
| `_REPORT` | Detailed analysis or test results | `TDD_CORE_MODULES_FINAL_REPORT.md` |
| `_SUMMARY` | High-level overview of work completed | `PAYMENT_INTEGRATION_COMPLETE_SUMMARY.md` |
| `_GUIDE` | Step-by-step instructions | `TWILIO_SETUP_GUIDE.md` |
| `_ANALYSIS` | In-depth investigation | `API_DUPLICATIONS_ANALYSIS.md` |
| `_AUDIT` | Quality or compliance review | `BACKEND_API_MVP_AUDIT_REPORT.md` |
| `_FIX` | Bug fix documentation | `CHECKOUT_AUTH_FIX_SUMMARY.md` |
| `_PLAN` | Implementation or strategy plan | `VENDOR_ORDER_MANAGEMENT_IMPLEMENTATION_PLAN.md` |
| `_CHECKLIST` | Task list or verification steps | `MVP_IMPLEMENTATION_CHECKLIST.md` |
| `_DIAGRAM` | Visual representation | `API_ARCHITECTURE_DIAGRAM.md` |
| `_REFERENCE` | Quick reference guide | `WOMPI_QUICK_REFERENCE.md` |

#### Category Prefixes

Common prefixes for grouping related documents:

| Prefix | Category | Example |
|--------|----------|---------|
| `TDD` | Test-Driven Development | `TDD_RED_PHASE_FIXES_SUMMARY.md` |
| `E2E` | End-to-End Testing | `E2E_TESTING_ARCHITECTURE.md` |
| `API` | API Documentation/Analysis | `API_DUPLICATIONS_ANALYSIS.md` |
| `MVP` | Minimum Viable Product | `MVP_CONSOLIDATED_REPORT.md` |
| `DATABASE` | Database-related | `DATABASE_SETUP.md` |
| `PAYMENT` | Payment systems | `PAYMENT_API_TEST_REPORT.md` |
| `VENDOR` | Vendor management | `VENDOR_REGISTRATION_GUIDE.md` |
| `BUYER` | Buyer features | `BUYER_DASHBOARD_EXECUTIVE_SUMMARY.md` |
| `INTEGRATION` | Third-party integrations | `INTEGRATION_TESTING_REPORT.md` |
| `CHECKOUT` | Checkout process | `CHECKOUT_VALIDATION_GUIDE.md` |
| `STOCK` | Inventory management | `STOCK_FIX_EXECUTIVE_SUMMARY.md` |
| `SHIPPING` | Shipping features | `SHIPPING_MVP_EXECUTIVE_SUMMARY.md` |

#### Special Document Names

Certain files have standardized names across directories:

| Filename | Purpose | Location |
|----------|---------|----------|
| `README.md` | Directory overview and navigation | Every major directory |
| `CHANGELOG.md` | Version history | Project root |
| `CONTRIBUTING.md` | Contribution guidelines | Project root |
| `LICENSE` | Software license | Project root |
| `.gitignore` | Git exclusions | Project root and subdirectories |

---

### Script Files (.py, .sh)

#### Python Scripts: `{action}_{target}.py`

**Format**: lowercase_with_underscores (snake_case)

**Structure**:
- `action`: What the script does (analyze, create, validate, test, deploy)
- `target`: What it operates on (backend, database, tests, api)

**Examples**:
```
✓ analyze_backend_structure.py
✓ create_superuser.py
✓ validate_user_create_modal.py
✓ api_coverage_analysis.py
✓ test_vendor_orders_quick.py

✗ AnalyzeBackend.py                (Wrong case for script)
✗ script1.py                       (No descriptive information)
✗ backend-analyzer.py              (Use underscores, not hyphens)
✗ do_stuff.py                      (Too vague)
```

#### Shell Scripts: `{action}_{target}.sh`

**Format**: lowercase_with_underscores (snake_case)

**Examples**:
```
✓ deploy_production.sh
✓ run_all_tests.sh
✓ backup_database.sh
✓ cleanup_logs.sh

✗ deploy.sh                        (Too vague - deploy what? where?)
✗ RUN_TESTS.sh                     (Wrong case)
✗ script.sh                        (No descriptive information)
```

#### Script Categories by Action

| Action Prefix | Purpose | Examples |
|---------------|---------|----------|
| `analyze_` | Code/system analysis | `analyze_backend_structure.py` |
| `create_` | Create resources | `create_superuser.py`, `create_schema.py` |
| `validate_` | Validation checks | `validate_user_create_modal.py` |
| `test_` | Testing scripts | `test_vendor_orders_quick.py` |
| `deploy_` | Deployment scripts | `deploy_production.sh` |
| `backup_` | Backup operations | `backup_database.sh` |
| `restore_` | Restore operations | `restore_database.sh` |
| `run_` | Execute processes | `run_all_tests.sh` |
| `cleanup_` | Maintenance/cleanup | `cleanup_logs.sh` |
| `generate_` | Generate artifacts | `generate_test_report.py` |

---

## Directory Naming Conventions

### Standard Directory Names: `lowercase-with-hyphens` (kebab-case)

**Rationale**:
- Lowercase avoids case-sensitivity issues across OS
- Hyphens are URL-friendly and readable
- Consistent with modern web development standards

**Examples**:
```
✓ docs/
✓ scripts/
✓ architecture/
✓ implementation/
✓ test-results/
✓ api-documentation/

✗ API_Documentation/               (Wrong case)
✗ test_results/                    (Use hyphens for directories)
✗ TestResults/                     (Wrong case)
```

### Top-Level Directories

Critical directories that must exist at project root:

| Directory | Purpose | Protected? |
|-----------|---------|------------|
| `app/` | Backend application code | YES |
| `frontend/` | Frontend application code | YES |
| `tests/` | Test suites | YES |
| `alembic/` | Database migrations | YES |
| `docs/` | All documentation | NO |
| `scripts/` | Automation scripts | NO |
| `.workspace/` | AI agent workspace | NO |
| `docker/` | Docker configurations | YES |

### Documentation Directories

Under `docs/`:

| Directory | Contents | Naming Pattern |
|-----------|----------|----------------|
| `architecture/` | System design docs | `system-design/`, `decisions/`, `diagrams/` |
| `guides/` | How-to documentation | `setup/`, `features/`, `integration/`, `testing/` |
| `reports/` | Historical reports | `testing/`, `implementation/`, `bugs/`, `audits/` |
| `executive/` | Executive summaries | Flat structure, no subdirs |
| `api/` | API documentation | `endpoints/`, `schemas/` |

### Scripts Directories

Under `scripts/`:

| Directory | Script Types | Examples |
|-----------|--------------|----------|
| `analysis/` | Code analysis | `analyze_*`, `validate_*` |
| `deployment/` | Deployment scripts | `deploy_*`, `rollback_*` |
| `database/` | DB operations | `create_*`, `backup_*`, `restore_*` |
| `maintenance/` | Maintenance tasks | `cleanup_*`, `health_check_*` |
| `testing/` | Test runners | `test_*`, `run_*_tests` |

---

## Time-Based Organization

### Quarterly Archives

For reports that accumulate over time, use quarterly directories:

**Format**: `YYYY-QN/` where N is the quarter (1-4)

**Examples**:
```
docs/reports/testing/
├── 2025-Q4/                       ✓ Current quarter
│   ├── TDD_CORE_MODULES_FINAL_REPORT.md
│   └── E2E_TESTING_SUMMARY.md
├── 2025-Q3/                       ✓ Previous quarter
│   └── INTEGRATION_TESTING_REPORT.md
└── archives/                      ✓ Older than 6 months
    ├── 2025-Q2/
    └── 2025-Q1/
```

**Archive Policy**:
- Keep current quarter + previous quarter visible
- Move reports older than 6 months to `archives/`
- Maintain quarterly structure within archives

### Date Suffixes (When Needed)

For documents where date is critical:

**Format**: `{DESCRIPTION}_YYYY-MM-DD.md`

**Use Cases**:
- Roadmap status updates
- Deployment records
- Security audits
- Performance benchmarks

**Examples**:
```
✓ ROADMAP_STATUS_UPDATE_2025-10-02.md
✓ SECURITY_AUDIT_2025-09-15.md
✓ PERFORMANCE_BENCHMARK_2025-10-01.md

✗ ROADMAP_10_02_25.md              (Ambiguous date format)
✗ ROADMAP_STATUS_v3.md             (Use dates, not versions)
```

**Date Format**: Always use ISO 8601 format `YYYY-MM-DD`

---

## Code Standardization (CEO Directive 2025-10-01)

### Technical Code: ENGLISH ONLY

All technical code elements must use English:

| Element | Language | Examples |
|---------|----------|----------|
| Variables | English | `user_email`, `product_price` |
| Functions | English | `create_order()`, `validate_payment()` |
| Classes | English | `UserModel`, `PaymentService` |
| API Endpoints | English | `/api/v1/products/`, `/api/v1/orders/` |
| Database Tables | English | `users`, `products`, `orders` |
| File Names (code) | English | `user_service.py`, `payment_handler.ts` |
| Comments (code) | English | `# Calculate tax based on location` |

**Examples**:
```python
# ✓ CORRECT - All English
@router.get("/api/v1/products/")
def get_products(db: Session):
    products = db.query(Product).all()
    return products

# ✗ WRONG - Spanish in code
@router.get("/api/v1/productos/")
def obtener_productos(db: Session):
    productos = db.query(Producto).all()
    return productos
```

### User-Facing Content: SPANISH

All user-facing content must use Spanish:

| Element | Language | Examples |
|---------|----------|----------|
| UI Text | Spanish | "Agregar al Carrito", "Finalizar Compra" |
| Error Messages | Spanish | "El correo es requerido" |
| Notifications | Spanish | "Pedido creado exitosamente" |
| Email Templates | Spanish | "Bienvenido a MeStore" |
| Documentation (user) | Spanish | User guides in Spanish |

**Examples**:
```typescript
// ✓ CORRECT - Spanish UI text, English code
function AddToCartButton() {
  return <button onClick={handleAddToCart}>
    Agregar al Carrito
  </button>
}

// ✗ WRONG - English UI text
function AddToCartButton() {
  return <button onClick={handleAddToCart}>
    Add to Cart
  </button>
}
```

### Deprecated Files (Migration Period)

Files being deprecated should be clearly marked:

**Format**: `{DEPRECATED}_{ORIGINAL_NAME}.py`

**Examples**:
```
DEPRECATED_productos.py            ✓ Clear deprecation marker
productos.py.old                   ✗ Ambiguous
productos_backup.py                ✗ Could be confused with backup
```

**Deprecation Timeline**:
- Week 1-2: Add deprecation warnings to code
- Week 3-6: Migration period, both versions coexist
- Week 7+: Remove deprecated versions

---

## Special Cases and Exceptions

### Configuration Files

Configuration files often have specific required names:

| File | Purpose | Naming |
|------|---------|--------|
| `.env` | Environment variables | Fixed name, required by tools |
| `docker-compose.yml` | Docker config | Fixed name, required by Docker |
| `package.json` | Node dependencies | Fixed name, required by npm |
| `requirements.txt` | Python dependencies | Fixed name, required by pip |
| `alembic.ini` | Alembic config | Fixed name, required by Alembic |
| `.gitignore` | Git exclusions | Fixed name, required by Git |

**Note**: These names cannot be changed as they are required by tools.

### Migration Files

Alembic migration files have auto-generated names:

**Format**: `{revision}_{slug}.py`

**Example**: `abc123def456_add_user_email_verification.py`

**Do not modify**: These are generated by Alembic and should not be renamed.

### Test Files

Test files follow framework conventions:

**Python (pytest)**:
```
test_{module}.py                   ✓ pytest standard
{module}_test.py                   ✓ Alternative pytest pattern
test_integration_{feature}.py      ✓ Specific test type
```

**JavaScript (Vitest)**:
```
{component}.test.ts                ✓ Vitest standard
{component}.test.tsx               ✓ React component tests
{module}.spec.ts                   ✓ Alternative pattern
```

---

## README File Standards

### Required Content Structure

Every `README.md` file should follow this structure:

```markdown
# [Directory Name]

## Overview
Brief description of what this directory contains (2-3 sentences)

## Contents
List of main subdirectories or file categories with descriptions

## Usage
How to use/navigate this section (if applicable)

## Related Documentation
Links to related docs or parent directories
```

### README Depth

| Directory Level | README Required? | Depth |
|----------------|------------------|-------|
| Top-level (docs/, scripts/) | YES | Comprehensive |
| Second-level (docs/guides/) | YES | Moderate |
| Third-level (docs/guides/setup/) | OPTIONAL | Brief if needed |

---

## Validation and Enforcement

### Pre-Commit Checks

Recommended automated checks:

1. **Filename Pattern Validation**
   - Documentation files match `{CATEGORY}_{DESCRIPTION}_{TYPE}.md`
   - Scripts match `{action}_{target}.{py|sh}`
   - No spaces in filenames

2. **Case Validation**
   - Documentation files in SCREAMING_SNAKE_CASE
   - Script files in snake_case
   - Directories in kebab-case

3. **Deprecated File Detection**
   - Flag files using deprecated naming patterns
   - Suggest correct naming convention

### Manual Review Checklist

Before committing new documentation or scripts:

- [ ] Filename follows established pattern for type
- [ ] Category/prefix is appropriate and consistent
- [ ] Case convention is correct
- [ ] Filename is descriptive and clear
- [ ] No version numbers or dates (unless required)
- [ ] File is in correct directory
- [ ] README updated if new category created

---

## Migration Guide

### Renaming Existing Files

When renaming files to match conventions:

1. **Update Git History Carefully**
   ```bash
   git mv old_name.md NEW_NAME.md
   git commit -m "refactor(docs): rename to follow naming conventions"
   ```

2. **Update All References**
   - Search codebase for old filename
   - Update all links in documentation
   - Update imports in code

3. **Add Redirect (if needed)**
   - For important docs, consider leaving redirect file
   - Or add link in parent README pointing to new location

### Batch Renaming Script

For mass renaming, use script with validation:

```bash
# Example script structure
for file in *.md; do
  # Validate new name
  # Check for conflicts
  # Rename file
  # Update references
done
```

---

## Examples and Anti-Patterns

### Good Examples

```
docs/reports/testing/2025-Q4/TDD_SECURITY_ANALYSIS_REPORT.md
scripts/analysis/analyze_backend_structure.py
docs/guides/setup/DATABASE_SETUP.md
docs/executive/MVP_EXECUTIVE_SUMMARY.md
scripts/deployment/deploy_production.sh
```

### Anti-Patterns to Avoid

```
✗ final_report_v3_FINAL.md         (Version numbers, redundancy)
✗ Testing Doc.md                   (Spaces, vague)
✗ script.py                        (No descriptive name)
✗ Stuff_To_Do.md                   (Unprofessional)
✗ README (2).md                    (Duplicate indicator)
✗ temp_file.md                     (Temporary files in repo)
✗ old_backup_copy.md               (Should be in git history)
```

---

## Conclusion

Consistent naming conventions are critical for:
- **Discoverability**: Find files quickly and predictably
- **Maintainability**: Understand purpose without opening file
- **Professionalism**: Present organized, enterprise-quality codebase
- **Scalability**: Support project growth without chaos

**Key Takeaways**:
1. Documentation: `SCREAMING_SNAKE_CASE` with clear category prefixes
2. Scripts: `snake_case` with action_target pattern
3. Directories: `kebab-case` for readability
4. Technical code: English only (CEO directive)
5. User content: Spanish only
6. Quarterly archives for time-based reports
7. Consistent README structure across project

When in doubt, follow existing patterns for similar files or consult this guide.
