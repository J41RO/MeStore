# 📋 COMMIT TEMPLATE - GIT CONTROL AI

## 🎯 MANDATORY COMMIT FORMAT

All commits during reorganization MUST follow this exact format:

```
type(scope): brief description in English

Workspace-Check: ✅ Consultado
Files: path/to/file1.md, path/to/file2.md
Agent: [agent-name]
Operation: [GIT_MV/CONSOLIDATE/ARCHIVE/UPDATE_REFS]
Protocol: [FOLLOWED/CONSULTATION/APPROVAL_OBTAINED]
Tests: [NOT_APPLICABLE/PASSED/FAILED]
Admin-Portal: NOT_APPLICABLE
Hook-Violations: NONE
History-Preserved: ✅ Verified with git log --follow

Changes:
- Specific change 1
- Specific change 2
- Specific change 3
```

## 📝 COMMIT TYPE DEFINITIONS

### For Reorganization:
- `docs(reorganization):` - Moving documentation files
- `chore(archive):` - Archiving obsolete files
- `refactor(consolidate):` - Consolidating duplicate docs
- `fix(references):` - Updating code references

### Examples:

#### 1. Moving files to docs/
```
docs(reorganization): Move setup guides to docs/guides/setup/

Workspace-Check: ✅ Consultado
Files: DATABASE_SETUP.md, SMS_GATEWAY_SETUP_GUIDE.md, TWILIO_SETUP_GUIDE.md
Agent: technical-debt-manager
Operation: GIT_MV
Protocol: FOLLOWED
Tests: NOT_APPLICABLE
Admin-Portal: NOT_APPLICABLE
Hook-Violations: NONE
History-Preserved: ✅ Verified with git log --follow

Changes:
- git mv DATABASE_SETUP.md docs/guides/setup/DATABASE_SETUP.md
- git mv SMS_GATEWAY_SETUP_GUIDE.md docs/guides/setup/SMS_GATEWAY_SETUP_GUIDE.md
- git mv TWILIO_SETUP_GUIDE.md docs/guides/setup/TWILIO_SETUP_GUIDE.md
- Preserved complete Git history for all files
```

#### 2. Archiving obsolete files
```
chore(archive): Archive duplicate E2E testing reports from 2025

Workspace-Check: ✅ Consultado
Files: E2E_TESTING_SUMMARY.md, BUYER_DASHBOARD_COMPLETION_SUMMARY.md
Agent: workflow-manager
Operation: ARCHIVE
Protocol: FOLLOWED
Tests: NOT_APPLICABLE
Admin-Portal: NOT_APPLICABLE
Hook-Violations: NONE
History-Preserved: ✅ Verified with git log --follow

Changes:
- git mv E2E_TESTING_SUMMARY.md archive/2025/E2E_TESTING_SUMMARY.md
- git mv BUYER_DASHBOARD_COMPLETION_SUMMARY.md archive/2025/BUYER_DASHBOARD_COMPLETION_SUMMARY.md
- Keeping E2E_TESTING_COMPLETE_SUMMARY.md as definitive version
```

#### 3. Consolidating duplicates
```
refactor(consolidate): Consolidate checkout fix reports

Workspace-Check: ✅ Consultado
Files: CHECKOUT_PSE_FIX_SUMMARY.md, CHECKOUT_AUTH_FIX_SUMMARY.md
Agent: technical-debt-manager
Operation: CONSOLIDATE
Protocol: FOLLOWED
Tests: NOT_APPLICABLE
Admin-Portal: NOT_APPLICABLE
Hook-Violations: NONE
History-Preserved: ✅ Both files preserved in git history

Changes:
- Created docs/reports/bugs/CHECKOUT_FIXES_CONSOLIDATED.md
- Merged content from CHECKOUT_PSE_FIX_SUMMARY.md (87% similar)
- Merged content from CHECKOUT_AUTH_FIX_SUMMARY.md
- Archived originals to archive/2025/
```

#### 4. Updating code references
```
fix(references): Update SAFE_API_MIGRATION_STRATEGY references in deprecated endpoints

Workspace-Check: ✅ Consultado
Files: app/api/v1/endpoints/vendedores.py, comisiones.py, pagos.py, productos.py
Agent: workflow-manager
Operation: UPDATE_REFS
Protocol: FOLLOWED
Tests: PASSED
Admin-Portal: NOT_APPLICABLE
Hook-Violations: NONE
History-Preserved: N/A (code change only)

Changes:
- Updated path from SAFE_API_MIGRATION_STRATEGY.md to docs/executive/SAFE_API_MIGRATION_STRATEGY.md
- Verified all 4 endpoints reference correct path
- Ran pytest to ensure no import errors
```

## 🚨 CRITICAL RULES

### ✅ REQUIRED:
1. Always use `git mv` (NEVER plain `mv`)
2. Verify history preserved: `git log --follow [file]`
3. Include all moved files in commit message
4. Specify operation type clearly
5. Run validation script before commit

### ❌ PROHIBITED:
1. NO plain `mv` commands
2. NO commits mixing code + reorganization
3. NO commits without proper format
4. NO force pushes to main
5. NO bypassing git-control-ai supervision

## 🔧 VALIDATION BEFORE COMMIT

Before each commit, RUN:
```bash
bash .workspace/departments/infrastructure/git-control-ai/git-operations/validation_protocol.sh
```

This will verify:
- ✅ Git mv usage (no plain mv)
- ✅ Protected files not modified
- ✅ Repository integrity
- ✅ History preservation
- ✅ No lost files

## 📊 COMMIT STATISTICS TRACKING

Git Control AI tracks:
- Total commits during reorganization
- Files moved with git mv
- History preservation rate
- Protected file violations (must be 0)
- Commit format compliance

---

**⚡ ENFORCEMENT**: git-control-ai has EXCLUSIVE authority
**🚨 VIOLATIONS**: Will be immediately blocked and corrected
**📝 DOCUMENTATION**: All operations logged in git-operations/

---

**Template Version**: 1.0
**Last Updated**: 2025-10-12
**Authority**: git-control-ai
