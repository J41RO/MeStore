# TOP 10 FILES TO KEEP IN ROOT DIRECTORY

**Purpose**: Quick reference for Phase 2/3 migration - these files MUST remain in project root
**Date**: 2025-10-12
**Analyst**: technical-debt-manager

---

## MANDATORY ROOT FILES (NEVER MOVE)

### 1. CLAUDE.md
- **Size**: 30 KB
- **Status**: PROTECTED - CRITICAL
- **Reason**: Primary project guide for all AI agents
- **References**: .workspace/SYSTEM_RULES.md, all agent workflows
- **Action**: NEVER MOVE

### 2. README.md
- **Size**: 11 KB
- **Status**: PROTECTED - CRITICAL
- **Reason**: Git repository default documentation, first impression
- **References**: GitHub/GitLab default view
- **Action**: NEVER MOVE

---

## TEMPORARILY IN ROOT (Move after updating references)

### 3. SAFE_API_MIGRATION_STRATEGY.md
- **Size**: 11 KB
- **Status**: REFERENCED IN CODE - HIGH PRIORITY
- **Reason**: Referenced in 4 deprecated API endpoint files
- **References**:
  - app/api/v1/endpoints/vendedores.py
  - app/api/v1/endpoints/comisiones.py
  - app/api/v1/endpoints/pagos.py
  - app/api/v1/endpoints/productos.py
- **Action**: Update all 4 files FIRST, then move to docs/executive/

---

## IMPORTANT EXECUTIVE DOCUMENTS (Consider keeping in root temporarily)

### 4. PRODUCTION_READINESS_REPORT.md
- **Size**: 33 KB
- **Status**: Executive-level, high visibility
- **Reason**: Critical for deployment decisions
- **Target**: docs/executive/ (after CEO review)
- **Action**: Keep in root until production deployment complete

### 5. MVP_EXECUTIVE_SUMMARY.md
- **Size**: 9 KB
- **Status**: Executive-level, high visibility
- **Reason**: Key stakeholder document
- **Target**: docs/executive/
- **Action**: Keep in root for 1-2 weeks, then move

### 6. CODE_QUALITY_EXECUTIVE_SUMMARY.md
- **Size**: 5 KB
- **Status**: Recent report (2025-10-12)
- **Reason**: Current quality assessment
- **Target**: docs/reports/audits/
- **Action**: Keep in root for 1 week, then move

---

## HIGH-VALUE REFERENCE DOCUMENTS

### 7. API_ARCHITECTURE_DIAGRAM.md
- **Size**: 29 KB
- **Status**: Frequently referenced
- **Reason**: Core system architecture documentation
- **Target**: docs/architecture/
- **Action**: Move to docs/ but create root-level link/shortcut

### 8. TODO_MVP_VENDOR_FLOW.md
- **Size**: 64 KB (LARGEST active doc)
- **Status**: Active development reference
- **Reason**: Comprehensive vendor feature roadmap
- **Target**: docs/guides/features/vendor-orders/
- **Action**: Move to docs/ after vendor orders feature complete

### 9. BACKEND_API_QUICK_SUMMARY.md
- **Size**: 7 KB
- **Status**: Quick reference for developers
- **Reason**: Frequently accessed API overview
- **Target**: docs/api/
- **Action**: Move to docs/ but update CLAUDE.md with new location

### 10. DATABASE_SETUP.md
- **Size**: 6 KB
- **Status**: Setup guide, frequently needed
- **Reason**: New developer onboarding
- **Target**: docs/guides/setup/
- **Action**: Move to docs/ but update CLAUDE.md and README.md with link

---

## DECISION MATRIX: KEEP IN ROOT VS MOVE TO DOCS

| Criteria | Keep in Root | Move to docs/ |
|----------|--------------|---------------|
| Referenced in code | ✅ YES | ❌ NO |
| Critical for all agents | ✅ YES | ❌ NO |
| Git default view | ✅ YES | ❌ NO |
| Executive visibility | ⚠️ TEMPORARY | After review |
| Developer reference | ⚠️ TEMPORARY | With link in README |
| Active development | ⚠️ TEMPORARY | After feature complete |
| Historical/archived | ❌ NO | ✅ YES |
| Duplicate/obsolete | ❌ NO | ✅ ARCHIVE |

---

## PHASE 2 PRIORITY ACTIONS

### IMMEDIATE (Day 1)
1. Update 4 API endpoint files to remove SAFE_API_MIGRATION_STRATEGY.md reference
2. Move SAFE_API_MIGRATION_STRATEGY.md to docs/executive/
3. Update CLAUDE.md with new location

### SHORT-TERM (Week 1)
4. Move CODE_QUALITY_EXECUTIVE_SUMMARY.md to docs/reports/audits/
5. Move API_ARCHITECTURE_DIAGRAM.md to docs/architecture/
6. Move BACKEND_API_QUICK_SUMMARY.md to docs/api/
7. Update CLAUDE.md and README.md with links to moved files

### MEDIUM-TERM (Weeks 2-4)
8. Move PRODUCTION_READINESS_REPORT.md to docs/executive/ (after deployment)
9. Move MVP_EXECUTIVE_SUMMARY.md to docs/executive/
10. Move TODO_MVP_VENDOR_FLOW.md to docs/guides/features/ (after vendor orders complete)
11. Move DATABASE_SETUP.md to docs/guides/setup/

---

## ROOT DIRECTORY FINAL STATE

After Phase 3 completion, root directory should contain:

```
/home/admin-jairo/MeStore/
├── CLAUDE.md (30 KB) ← PERMANENT
├── README.md (11 KB) ← PERMANENT
├── [Quick links section in README to key docs/]
├── reorganization_inventory.json (Phase 1 output)
├── PHASE_1_EXECUTIVE_SUMMARY.md (Phase 1 report)
├── [Maximum 3-5 other critical docs temporarily]
└── [All other .md files moved to docs/ or .archive/]
```

**Target**: Root directory with 2 permanent files + 3-5 temporary high-priority files = 5-7 total .md files

**Current State**: 122 .md files in root
**Target State**: 5-7 .md files in root (94% reduction)

---

## VALIDATION CHECKLIST

Before moving ANY of these files, verify:

- [ ] No references in Python source code (search `grep -r "FILENAME.md" app/`)
- [ ] No references in TypeScript/React code (search `grep -r "FILENAME.md" frontend/src/`)
- [ ] No references in shell scripts (search `grep -r "FILENAME.md" scripts/`)
- [ ] No references in .workspace/ files
- [ ] Update CLAUDE.md if file is frequently referenced
- [ ] Update README.md if file is onboarding-critical
- [ ] Create redirect/link if file is frequently accessed
- [ ] Notify all agents if file location changes

---

**Last Updated**: 2025-10-12
**Next Review**: Before Phase 2 start
**Owner**: technical-debt-manager
