# FILE PLACEMENT GUIDE - MeStore

## Purpose

This guide provides clear, actionable rules for determining where every type of file belongs in the MeStore project structure. Use this as a quick reference when creating or organizing files.

---

## Quick Decision Tree

```
Is it code that runs the application?
├─ YES → app/ or frontend/ (existing structure)
└─ NO → Continue...

Is it a test file?
├─ YES → tests/ (existing structure)
└─ NO → Continue...

Is it documentation (.md file)?
├─ YES → See "Documentation Placement" below
└─ NO → Continue...

Is it a script (.py, .sh)?
├─ YES → See "Script Placement" below
└─ NO → Continue...

Is it configuration?
├─ YES → See "Configuration Placement" below
└─ NO → Ask System Architect
```

---

## Documentation Placement

### Decision Matrix for .md Files

| If the document is... | Place it in... | Example |
|----------------------|----------------|---------|
| System architecture, design decisions | `docs/architecture/` | API_ARCHITECTURE_DIAGRAM.md |
| Setup/installation instructions | `docs/guides/setup/` | DATABASE_SETUP.md |
| Feature usage guide | `docs/guides/features/` | VENDOR_REGISTRATION_GUIDE.md |
| Third-party integration guide | `docs/guides/integration/` | TWILIO_SETUP_GUIDE.md |
| Testing procedures/how-to | `docs/guides/testing/` | E2E_TESTING_GUIDE.md |
| Test execution results | `docs/reports/testing/YYYY-QN/` | TDD_CORE_MODULES_FINAL_REPORT.md |
| Feature implementation report | `docs/reports/implementation/YYYY-QN/` | PAYMENT_INTEGRATION_COMPLETE_SUMMARY.md |
| Bug fix documentation | `docs/reports/bugs/YYYY-QN/` | CHECKOUT_AUTH_FIX_SUMMARY.md |
| Code/system audit | `docs/reports/audits/YYYY-QN/` | API_DUPLICATIONS_ANALYSIS.md |
| Performance analysis | `docs/reports/performance/YYYY-QN/` | DATABASE_PERFORMANCE_ANALYSIS.md |
| Executive summary | `docs/executive/` | MVP_EXECUTIVE_SUMMARY.md |
| API reference documentation | `docs/api/` | endpoints/products.md |

### Detailed Documentation Categories

#### 1. Architecture Documentation → `docs/architecture/`

**What goes here**:
- System-level design documents
- Architecture Decision Records (ADRs)
- Technology stack choices and justifications
- Integration patterns between major components
- Scalability and performance architecture
- Security architecture documentation
- Visual system diagrams

**What does NOT go here**:
- Feature-specific guides (→ `docs/guides/features/`)
- Implementation reports (→ `docs/reports/implementation/`)
- API endpoint documentation (→ `docs/api/`)

**Examples**:
```
✓ docs/architecture/system-design/API_ARCHITECTURE_DIAGRAM.md
✓ docs/architecture/decisions/ADR-001-API-VERSIONING.md
✓ docs/architecture/diagrams/system-overview.png

✗ docs/architecture/PAYMENT_INTEGRATION_GUIDE.md    → docs/guides/integration/
✗ docs/architecture/TDD_TESTING_REPORT.md           → docs/reports/testing/
```

#### 2. Setup Guides → `docs/guides/setup/`

**What goes here**:
- Initial project setup instructions
- Development environment configuration
- Database setup and initialization
- External service configuration (SMS, payments, etc.)
- Prerequisites and dependencies
- Environment variable setup

**What does NOT go here**:
- Feature usage (→ `docs/guides/features/`)
- Test execution results (→ `docs/reports/testing/`)
- Architecture decisions (→ `docs/architecture/`)

**Decision criteria**: Does this help someone set up the project for the first time?

**Examples**:
```
✓ docs/guides/setup/DATABASE_SETUP.md
✓ docs/guides/setup/TWILIO_SETUP_GUIDE.md
✓ docs/guides/setup/DEVELOPMENT_ENVIRONMENT.md
✓ docs/guides/setup/QUICK_START.md

✗ docs/guides/setup/PAYMENT_TESTING_RESULTS.md      → docs/reports/testing/
✗ docs/guides/setup/VENDOR_DASHBOARD_USAGE.md       → docs/guides/features/
```

#### 3. Feature Guides → `docs/guides/features/`

**What goes here**:
- How to use specific features
- Feature workflows and user journeys
- Configuration options for features
- Best practices for feature usage
- Troubleshooting common issues

**What does NOT go here**:
- Implementation reports (→ `docs/reports/implementation/`)
- Test results (→ `docs/reports/testing/`)
- External service setup (→ `docs/guides/integration/`)

**Decision criteria**: Does this explain how to use or implement a specific feature?

**Examples**:
```
✓ docs/guides/features/VENDOR_REGISTRATION_GUIDE.md
✓ docs/guides/features/CHECKOUT_VALIDATION_GUIDE.md
✓ docs/guides/features/SHOPPING_CART_USAGE.md
✓ docs/guides/features/ORDER_MANAGEMENT.md

✗ docs/guides/features/CHECKOUT_BUG_FIX.md          → docs/reports/bugs/
✗ docs/guides/features/WOMPI_API_SETUP.md           → docs/guides/integration/
```

#### 4. Integration Guides → `docs/guides/integration/`

**What goes here**:
- Third-party service integration instructions
- Payment gateway setup and configuration
- SMS/Email service integration
- WhatsApp API integration
- Authentication provider setup (OAuth, etc.)
- API keys and credentials management

**What does NOT go here**:
- Internal feature guides (→ `docs/guides/features/`)
- Integration test results (→ `docs/reports/testing/`)
- Architecture decisions about integrations (→ `docs/architecture/`)

**Decision criteria**: Is this about integrating an external service?

**Examples**:
```
✓ docs/guides/integration/WOMPI_QUICK_REFERENCE.md
✓ docs/guides/integration/TWILIO_SMS_INTEGRATION.md
✓ docs/guides/integration/PAYU_PAYMENT_SETUP.md
✓ docs/guides/integration/WHATSAPP_API_INTEGRATION.md

✗ docs/guides/integration/DATABASE_SETUP.md         → docs/guides/setup/
✗ docs/guides/integration/PAYMENT_TEST_RESULTS.md   → docs/reports/testing/
```

#### 5. Testing Guides → `docs/guides/testing/`

**What goes here**:
- How to write tests (TDD, E2E, unit, integration)
- Testing best practices and patterns
- How to run specific test suites
- Testing workflow documentation
- Coverage requirements and standards

**What does NOT go here**:
- Test execution results (→ `docs/reports/testing/`)
- Testing tool setup (→ `docs/guides/setup/`)
- Bug fixes (→ `docs/reports/bugs/`)

**Decision criteria**: Does this teach how to write or run tests?

**Examples**:
```
✓ docs/guides/testing/TDD_WORKFLOW.md
✓ docs/guides/testing/E2E_TESTING_GUIDE.md
✓ docs/guides/testing/PRODUCT_DETAIL_TESTING_GUIDE.md
✓ docs/guides/testing/COVERAGE_STANDARDS.md

✗ docs/guides/testing/TDD_TEST_RESULTS_2025.md      → docs/reports/testing/
✗ docs/guides/testing/PYTEST_INSTALLATION.md        → docs/guides/setup/
```

#### 6. Testing Reports → `docs/reports/testing/YYYY-QN/`

**What goes here**:
- Test execution results and summaries
- Coverage reports
- Test failure analysis
- Performance testing results
- Regression testing reports

**What does NOT go here**:
- How to write tests (→ `docs/guides/testing/`)
- Bug fix documentation (→ `docs/reports/bugs/`)
- Implementation reports (→ `docs/reports/implementation/`)

**Decision criteria**: Is this the result of running tests?

**Organization**: Group by quarter (YYYY-QN), move to archives/ after 6 months

**Examples**:
```
✓ docs/reports/testing/2025-Q4/TDD_CORE_MODULES_FINAL_REPORT.md
✓ docs/reports/testing/2025-Q4/E2E_TESTING_COMPLETE_SUMMARY.md
✓ docs/reports/testing/2025-Q4/INTEGRATION_TESTING_REPORT.md
✓ docs/reports/testing/2025-Q4/PERFORMANCE_TESTING_COVERAGE_ACCELERATION_REPORT.md

✗ docs/reports/testing/2025-Q4/HOW_TO_RUN_E2E_TESTS.md  → docs/guides/testing/
✗ docs/reports/testing/2025-Q4/CHECKOUT_BUG_FIX.md       → docs/reports/bugs/
```

#### 7. Implementation Reports → `docs/reports/implementation/YYYY-QN/`

**What goes here**:
- Feature implementation completion summaries
- Integration implementation reports
- Dashboard/UI component implementation
- System component deployment reports
- Migration completion reports

**What does NOT go here**:
- How-to guides (→ `docs/guides/`)
- Test results (→ `docs/reports/testing/`)
- Bug fixes (→ `docs/reports/bugs/`)

**Decision criteria**: Does this document the completion of a feature or component?

**Organization**: Group by quarter (YYYY-QN), move to archives/ after 6 months

**Examples**:
```
✓ docs/reports/implementation/2025-Q4/PAYMENT_INTEGRATION_COMPLETE_SUMMARY.md
✓ docs/reports/implementation/2025-Q4/BUYER_DASHBOARD_COMPLETION_SUMMARY.md
✓ docs/reports/implementation/2025-Q4/VENDOR_ORDER_MANAGEMENT_EXECUTIVE_SUMMARY.md
✓ docs/reports/implementation/2025-Q4/SMS_GATEWAY_IMPLEMENTATION_SUMMARY.md

✗ docs/reports/implementation/2025-Q4/PAYMENT_SETUP_GUIDE.md     → docs/guides/integration/
✗ docs/reports/implementation/2025-Q4/PAYMENT_TEST_RESULTS.md    → docs/reports/testing/
```

#### 8. Bug Fix Reports → `docs/reports/bugs/YYYY-QN/`

**What goes here**:
- Bug analysis and investigation
- Fix implementation documentation
- Verification and testing of fixes
- Post-fix validation reports
- Root cause analysis

**What does NOT go here**:
- General testing reports (→ `docs/reports/testing/`)
- Feature implementations (→ `docs/reports/implementation/`)
- Troubleshooting guides (→ `docs/guides/features/`)

**Decision criteria**: Does this document the resolution of a bug?

**Organization**: Group by quarter (YYYY-QN), move to archives/ after 6 months

**Examples**:
```
✓ docs/reports/bugs/2025-Q4/CHECKOUT_AUTH_FIX_SUMMARY.md
✓ docs/reports/bugs/2025-Q4/RATING_NULL_SAFETY_FIX.md
✓ docs/reports/bugs/2025-Q4/SHIPPING_FORM_VALIDATION_FIX.md
✓ docs/reports/bugs/2025-Q4/PSE_LOOP_INFINITO_FIX_VERIFICATION.md

✗ docs/reports/bugs/2025-Q4/GENERAL_E2E_TEST_RESULTS.md  → docs/reports/testing/
✗ docs/reports/bugs/2025-Q4/NEW_FEATURE_IMPLEMENTATION.md → docs/reports/implementation/
```

#### 9. Audit Reports → `docs/reports/audits/YYYY-QN/`

**What goes here**:
- Code quality audits
- Security audits
- Architecture reviews
- API analysis and optimization
- UX/UI audits
- Performance audits
- Compliance audits

**What does NOT go here**:
- Architecture design docs (→ `docs/architecture/`)
- Implementation reports (→ `docs/reports/implementation/`)
- Bug fixes (→ `docs/reports/bugs/`)

**Decision criteria**: Is this an analysis or review of existing code/systems?

**Organization**: Group by quarter (YYYY-QN), move to archives/ after 6 months

**Examples**:
```
✓ docs/reports/audits/2025-Q4/API_DUPLICATIONS_ANALYSIS.md
✓ docs/reports/audits/2025-Q4/BACKEND_STRUCTURE_ANALYSIS.md
✓ docs/reports/audits/2025-Q4/UX_UI_MVP_AUDIT_REPORT.md
✓ docs/reports/audits/2025-Q4/PUBLIC_CATALOG_AUDIT.md

✗ docs/reports/audits/2025-Q4/NEW_API_ARCHITECTURE.md        → docs/architecture/
✗ docs/reports/audits/2025-Q4/BUG_FIX_VERIFICATION.md       → docs/reports/bugs/
```

#### 10. Performance Reports → `docs/reports/performance/YYYY-QN/`

**What goes here**:
- Performance benchmarks and analysis
- Load testing results
- Database query optimization reports
- Frontend performance analysis
- API response time measurements
- Scalability testing

**What does NOT go here**:
- Performance architecture design (→ `docs/architecture/`)
- Performance testing guides (→ `docs/guides/testing/`)
- General test results (→ `docs/reports/testing/`)

**Decision criteria**: Is this measuring and analyzing system performance?

**Organization**: Group by quarter (YYYY-QN), move to archives/ after 6 months

**Examples**:
```
✓ docs/reports/performance/2025-Q4/DATABASE_PERFORMANCE_ANALYSIS.md
✓ docs/reports/performance/2025-Q4/FRONTEND_LOAD_TIME_REPORT.md
✓ docs/reports/performance/2025-Q4/API_RESPONSE_TIME_BENCHMARK.md
✓ docs/reports/performance/2025-Q4/LOAD_TESTING_1000_USERS.md

✗ docs/reports/performance/2025-Q4/CACHING_ARCHITECTURE.md      → docs/architecture/
✗ docs/reports/performance/2025-Q4/HOW_TO_RUN_LOAD_TESTS.md    → docs/guides/testing/
```

#### 11. Executive Summaries → `docs/executive/`

**What goes here**:
- High-level summaries for stakeholders
- Strategic roadmap documents
- MVP status and completion reports
- Business-focused technical summaries
- Project milestone reports
- Quarterly business reviews

**What does NOT go here**:
- Technical implementation details (→ `docs/reports/implementation/`)
- Detailed test results (→ `docs/reports/testing/`)
- Technical architecture (→ `docs/architecture/`)

**Decision criteria**: Is this written for non-technical stakeholders or executives?

**Characteristics**:
- Less technical jargon
- Business impact focused
- Visual summaries preferred
- Strategic recommendations

**Organization**: Flat structure, no subdirectories

**Examples**:
```
✓ docs/executive/MVP_EXECUTIVE_SUMMARY.md
✓ docs/executive/PAYMENT_API_TESTING_EXECUTIVE_SUMMARY.md
✓ docs/executive/QA_FIXES_EXECUTIVE_SUMMARY.md
✓ docs/executive/ROADMAP_STATUS_UPDATE_2025-10-02.md

✗ docs/executive/DETAILED_API_ARCHITECTURE_DIAGRAM.md    → docs/architecture/
✗ docs/executive/FULL_TEST_COVERAGE_REPORT.md            → docs/reports/testing/
```

#### 12. API Documentation → `docs/api/`

**What goes here**:
- API endpoint reference documentation
- Request/response schemas
- Authentication documentation
- API versioning information
- Rate limiting documentation
- Example API calls and responses

**What does NOT go here**:
- Architecture decisions (→ `docs/architecture/`)
- Integration guides (→ `docs/guides/integration/`)
- API test results (→ `docs/reports/testing/`)

**Decision criteria**: Is this reference documentation for API consumers?

**Organization**:
- `endpoints/` - Endpoint documentation by resource
- `schemas/` - Data model definitions

**Examples**:
```
✓ docs/api/endpoints/products.md
✓ docs/api/endpoints/auth.md
✓ docs/api/schemas/user.md
✓ docs/api/openapi.json

✗ docs/api/HOW_TO_INTEGRATE_PAYMENTS.md        → docs/guides/integration/
✗ docs/api/API_TEST_RESULTS.md                 → docs/reports/testing/
```

---

## Script Placement

### Decision Matrix for Scripts

| If the script... | Place it in... | Example |
|-----------------|----------------|---------|
| Analyzes code/system | `scripts/analysis/` | analyze_backend_structure.py |
| Deploys to environment | `scripts/deployment/` | deploy_production.sh |
| Manages database | `scripts/database/` | create_superuser.py |
| Performs maintenance | `scripts/maintenance/` | cleanup_logs.sh |
| Runs tests | `scripts/testing/` | test_vendor_orders_quick.py |

### Detailed Script Categories

#### 1. Analysis Scripts → `scripts/analysis/`

**What goes here**:
- Code structure analysis
- Test coverage calculation
- API endpoint discovery
- Dependency analysis
- Code quality checks
- Security vulnerability scanning

**Decision criteria**: Does this analyze existing code or systems?

**Examples**:
```
✓ scripts/analysis/analyze_backend_structure.py
✓ scripts/analysis/api_coverage_analysis.py
✓ scripts/analysis/validate_user_create_modal.py
✓ scripts/analysis/find_unused_imports.py

✗ scripts/analysis/run_tests.py              → scripts/testing/
✗ scripts/analysis/deploy.py                 → scripts/deployment/
```

#### 2. Deployment Scripts → `scripts/deployment/`

**What goes here**:
- Production deployment automation
- Staging deployment scripts
- Rollback procedures
- Pre-deployment validation
- Post-deployment verification
- Environment configuration

**Decision criteria**: Is this used to deploy the application?

**Examples**:
```
✓ scripts/deployment/deploy_production.sh
✓ scripts/deployment/deploy_staging.sh
✓ scripts/deployment/rollback.sh
✓ scripts/deployment/pre_deploy_check.py

✗ scripts/deployment/backup_database.sh      → scripts/database/
✗ scripts/deployment/run_tests.sh            → scripts/testing/
```

#### 3. Database Scripts → `scripts/database/`

**What goes here**:
- Database schema creation
- Superuser/admin creation
- Data seeding
- Backup and restore operations
- Database cleanup
- Manual migrations (outside Alembic)

**Decision criteria**: Does this interact with the database directly?

**Note**: Alembic migrations go in `alembic/versions/`, not here

**Examples**:
```
✓ scripts/database/create_superuser.py
✓ scripts/database/create_schema.py
✓ scripts/database/backup_db.sh
✓ scripts/database/restore_db.sh
✓ scripts/database/seed_test_data.py

✗ scripts/database/deploy_to_production.sh   → scripts/deployment/
✗ scripts/database/analyze_queries.py        → scripts/analysis/
```

#### 4. Maintenance Scripts → `scripts/maintenance/`

**What goes here**:
- Log rotation and cleanup
- Cache invalidation
- Temporary file removal
- System health checks
- Disk space monitoring
- Regular cleanup tasks

**Decision criteria**: Is this routine maintenance or system upkeep?

**Examples**:
```
✓ scripts/maintenance/cleanup_logs.sh
✓ scripts/maintenance/clear_cache.py
✓ scripts/maintenance/health_check.py
✓ scripts/maintenance/remove_old_uploads.sh

✗ scripts/maintenance/create_user.py         → scripts/database/
✗ scripts/maintenance/deploy.sh              → scripts/deployment/
```

#### 5. Testing Scripts → `scripts/testing/`

**What goes here**:
- Test suite execution
- Quick validation tests
- Test report generation
- Coverage report creation
- Performance/load testing
- Integration test runners

**Decision criteria**: Does this run tests or generate test reports?

**Examples**:
```
✓ scripts/testing/run_all_tests.sh
✓ scripts/testing/test_vendor_orders_quick.py
✓ scripts/testing/generate_coverage_report.py
✓ scripts/testing/quick_smoke_test.py

✗ scripts/testing/analyze_test_code.py       → scripts/analysis/
✗ scripts/testing/backup_test_db.sh          → scripts/database/
```

---

## Configuration Placement

### Configuration Files

| File Type | Location | Example |
|-----------|----------|---------|
| Environment variables | Project root | `.env`, `.env.example`, `.env.production` |
| Docker configuration | Project root | `docker-compose.yml`, `Dockerfile` |
| Python dependencies | Project root | `requirements.txt`, `requirements_production.txt` |
| Node dependencies | `frontend/` | `package.json` |
| Alembic config | Project root | `alembic.ini` |
| Git configuration | Project root | `.gitignore` |
| Build tools | Project root | `Makefile`, `setup.py` |
| TypeScript config | `frontend/` | `tsconfig.json` |
| Vite config | `frontend/` | `vite.config.ts` |
| Pytest config | Project root | `pytest.ini`, `.coveragerc` |

**Rule**: Configuration files have required names and locations by their tools. Do not move them.

---

## Workspace Placement

### .workspace/ Organization

| Content Type | Location | Example |
|-------------|----------|---------|
| Global rules | `.workspace/` | `SYSTEM_RULES.md`, `PROTECTED_FILES.md` |
| CEO directives | `.workspace/core/directives/` | `CODE_STANDARDIZATION.md` |
| Development protocols | `.workspace/core/protocols/` | `COMMIT_TEMPLATE.md` |
| Document templates | `.workspace/core/templates/` | `ADR_TEMPLATE.md` |
| Agent offices | `.workspace/departments/{dept}/{agent}/` | `departments/backend/backend-framework-ai/` |
| Historical data | `.workspace/archives/` | `old-departments/`, `completed-projects/` |

**Rule**: .workspace/ is for AI agent coordination only. User-facing docs go in `docs/`

---

## Special Cases

### Where do these files go?

| File Description | Correct Location | Reasoning |
|------------------|------------------|-----------|
| Project README | `README.md` (root) | Standard entry point |
| Claude instructions | `CLAUDE.md` (root) | Required by AI agents |
| Roadmap documents | `docs/executive/` | Strategic, high-level |
| Migration guides | `docs/guides/setup/` if initial, `docs/reports/implementation/` if completed | Context-dependent |
| Architecture Decision Record | `docs/architecture/decisions/` | Architectural documentation |
| Deprecation notices | Same location as original file, update content | Keep context together |
| Temporary analysis | Should not commit, or `docs/reports/audits/` if valuable | Avoid clutter |
| Meeting notes | `.workspace/` or external system | Not code documentation |
| Screenshots | `docs/{category}/images/` | With related documentation |

---

## Archive Policy

### When to Archive

Move documents to archives/ subdirectory when:
- Report is older than 6 months
- Feature has been deprecated
- Implementation is no longer relevant
- Historical reference only

### Archive Structure

```
docs/reports/testing/
├── 2025-Q4/          ← Current quarter
├── 2025-Q3/          ← Recent (keep visible)
└── archives/
    ├── 2025-Q2/      ← Archived
    ├── 2025-Q1/
    └── 2024-Q4/
```

**Rule**: Keep current quarter + previous quarter visible, archive the rest

---

## Quick Reference Cheat Sheet

### Common File Types

```
Test result?           → docs/reports/testing/YYYY-QN/
Feature completed?     → docs/reports/implementation/YYYY-QN/
Bug fixed?             → docs/reports/bugs/YYYY-QN/
Code audit?            → docs/reports/audits/YYYY-QN/
Performance test?      → docs/reports/performance/YYYY-QN/

Setup guide?           → docs/guides/setup/
Feature guide?         → docs/guides/features/
Integration guide?     → docs/guides/integration/
Testing guide?         → docs/guides/testing/

Architecture doc?      → docs/architecture/
Executive summary?     → docs/executive/
API reference?         → docs/api/

Analysis script?       → scripts/analysis/
Deploy script?         → scripts/deployment/
Database script?       → scripts/database/
Maintenance script?    → scripts/maintenance/
Test script?           → scripts/testing/
```

---

## Validation Checklist

Before committing a new file, verify:

- [ ] File is in the correct top-level directory (docs/, scripts/, app/, etc.)
- [ ] File is in the correct subcategory
- [ ] Filename follows naming conventions
- [ ] Quarterly organization used if applicable
- [ ] README updated if new category created
- [ ] No duplicate files in multiple locations
- [ ] Links in documentation point to new location
- [ ] File doesn't belong in archives/ already

---

## When in Doubt

**Ask these questions**:

1. **Is this temporary?** → Don't commit, or add to `.gitignore`
2. **Is this for developers?** → `docs/` or code comments
3. **Is this for executives?** → `docs/executive/`
4. **Is this automated?** → `scripts/`
5. **Is this about AI agents?** → `.workspace/`
6. **Is this code?** → `app/` or `frontend/`
7. **Is this a test?** → `tests/`
8. **Is this configuration?** → Root or appropriate config directory
9. **Still unsure?** → Ask System Architect AI

---

## Conclusion

This guide provides clear rules for file placement across the MeStore project. When adding new files, follow the decision trees and criteria to ensure consistent organization.

**Key Principles**:
1. **Guides teach, Reports document** - Guides are how-to, reports are what happened
2. **Quarter-based archives** - Time-based reports use YYYY-QN structure
3. **Flat executive directory** - Executive summaries don't need subdirectories
4. **Scripts by function** - Scripts organized by what they do, not what they touch
5. **Configuration stays put** - Don't move files required by tools

**Remember**: A well-organized codebase is easier to navigate, maintain, and scale. Take the extra minute to place files correctly the first time.
