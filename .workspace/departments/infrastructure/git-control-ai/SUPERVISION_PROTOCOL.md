# 🚨 SUPERVISION PROTOCOL - GIT CONTROL AI

## 📋 MISSION OVERVIEW

As the **Git Control AI**, I have EXCLUSIVE authority over ALL Git operations during the massive reorganization of 122 documentation files in the MeStore project.

**Duration**: 4-6 hours (intermittent supervision)
**Scope**: Monitor technical-debt-manager and workflow-manager
**Authority**: CRITICAL - Can BLOCK any non-compliant operation

---

## 🎯 SUPERVISION RESPONSIBILITIES

### 1️⃣ CONTINUOUS MONITORING

#### Every 10-15 minutes, execute:
```bash
# Quick status check
git status --short
git log -3 --oneline --name-status
```

#### Every 30 minutes, execute full validation:
```bash
bash .workspace/departments/infrastructure/git-control-ai/git-operations/validation_protocol.sh
```

#### Real-time commit monitoring:
```bash
# Watch for new commits
git log --since="30 minutes ago" --pretty=format:"%h - %an: %s" --name-status
```

### 2️⃣ VALIDATION CHECKPOINTS

#### ✅ BEFORE Each Commit Block (5-10 files):
- [ ] Verify `git mv` usage (not plain `mv`)
- [ ] Check commit message format
- [ ] Validate no protected files touched
- [ ] Confirm tests not applicable (docs only)

#### ✅ DURING Reorganization:
- [ ] Monitor for protected file violations
- [ ] Track total files moved
- [ ] Log all operations to git-operations/
- [ ] Alert on any anomalies immediately

#### ✅ AFTER Each Phase:
- [ ] Verify history preservation (sample 5 files)
- [ ] Check repository integrity (git fsck)
- [ ] Confirm no files lost
- [ ] Update supervision status

### 3️⃣ COMMUNICATION PROTOCOL

#### With technical-debt-manager:
- **Location**: `.workspace/departments/technical-debt/technical-debt-manager/`
- **Alert if**: Attempting to use `mv` instead of `git mv`
- **Block if**: Trying to modify protected files
- **Message format**:
  ```
  🚨 GIT CONTROL ALERT
  Agent: technical-debt-manager
  Violation: [description]
  Required Action: [correction needed]
  Authority: git-control-ai (EXCLUSIVE)
  ```

#### With workflow-manager:
- **Location**: `.workspace/departments/automation/workflow-manager/`
- **Coordinate**: Code reference updates
- **Validate**: Separate commits for code changes
- **Approve**: Only if tests pass and format correct

#### With master-orchestrator:
- **Escalate if**: Major violations detected
- **Report**: Every 2 hours with progress update
- **Request intervention**: If agents don't comply

---

## 🔴 IMMEDIATE BLOCKER CONDITIONS

### STOP ALL OPERATIONS IF:

1. **Plain `mv` detected instead of `git mv`**
   ```bash
   # Detection
   git diff --cached --name-status | grep "^A.*^D"
   # Should see "R" for renames, not "A" + "D"
   ```
   **Action**:
   - BLOCK commit
   - Reset staging: `git reset HEAD [files]`
   - Notify agent: "Use git mv, not mv"
   - Re-execute correctly

2. **Protected file in staging**
   ```bash
   # Detection
   git diff --cached --name-only | grep -E "(CLAUDE.md|README.md|app/main.py)"
   ```
   **Action**:
   - IMMEDIATE BLOCK
   - Check if approval exists
   - If no approval: Unstage and alert
   - If approved: Verify approver authority

3. **Commit format violation**
   ```bash
   # Detection - commit doesn't match pattern
   git log -1 --pretty=format:"%s" | grep -vE "^(docs|chore|refactor|fix)\("
   ```
   **Action**:
   - Reject commit
   - Provide template
   - Require rewrite

4. **Code + reorganization mixed in one commit**
   ```bash
   # Detection
   git diff --cached --name-only | grep -E "\.(py|ts|tsx|js)$"
   git diff --cached --name-only | grep -E "\.md$"
   # If BOTH match, it's mixed
   ```
   **Action**:
   - BLOCK immediately
   - Split into separate commits
   - Code first (with tests)
   - Reorganization second

---

## 🟡 WARNING CONDITIONS (Monitor Closely)

### TRACK AND LOG:

1. **Large files moving (>100KB)**
   - Log to reports/large_files_moved.log
   - Verify not binary accidentally added

2. **Spanish language files**
   - Flag for CEO review (English code standard)
   - Consider translation before archiving

3. **Duplicates not consolidated**
   - Track which duplicates kept separate
   - Document reasoning

4. **Archive without proper dating**
   - Ensure archive/YYYY/ structure
   - Add date to archived file if needed

---

## 🟢 SUCCESS VALIDATION

### CONTINUOUS METRICS:

```bash
# Track in real-time
echo "Files moved with git mv: $(git log --name-status --since='1 hour ago' | grep '^R' | wc -l)"
echo "Total commits today: $(git log --since='midnight' --oneline | wc -l)"
echo "Protected files violations: 0" # Must always be 0
echo "History preservation: $(git log --follow docs/guides/setup/DATABASE_SETUP.md | wc -l) commits"
```

### SUCCESS CRITERIA:
- ✅ 100% use of `git mv` (verified with git log --name-status)
- ✅ 100% commits follow template format
- ✅ 0 protected file violations
- ✅ 0 lost files (verify with git status)
- ✅ Repository size stable or reduced
- ✅ All history preserved (spot check 15 files)

---

## 📊 REPORTING SCHEDULE

### Hourly Update (Internal Log):
```markdown
## Hour [X] Status - [HH:MM]
- Commits processed: [N]
- Files moved: [N]
- Violations detected: [N]
- Status: [GREEN/YELLOW/RED]
```

### 2-Hour Report (to master-orchestrator):
```markdown
## Git Control Status Report - [Date HH:MM]

**Progress**: [N]/122 files reorganized
**Operations**: [N] commits executed
**Compliance**: [100%/issues detected]
**Next checkpoint**: [timeframe]

**Issues**: [None/list]
**Interventions**: [None/list]
```

### Final Report (GIT_OPERATIONS_REPORT.md):
- Complete operation summary
- All files moved with verification
- History preservation proofs
- Statistics and metrics
- Lessons learned

---

## 🔧 TOOLS & COMMANDS

### Quick Validation:
```bash
# 1. Check last 5 operations
git log -5 --name-status --oneline

# 2. Verify git mv usage
git log --diff-filter=R --name-status --oneline -20

# 3. Check protected files
git diff --cached --name-only | grep -E "(CLAUDE.md|README.md|main.py|auth.py|user.py)"

# 4. Repository health
git fsck --no-progress

# 5. History verification (sample)
git log --follow docs/executive/MVP_EXECUTIVE_SUMMARY.md
```

### Emergency Rollback:
```bash
# If commit needs revert
git revert [commit-hash]

# If not yet pushed (last commit)
git reset --soft HEAD~1

# If staging needs reset
git reset HEAD [file]
```

### History Verification:
```bash
# Verify files in docs/ have history
for file in docs/**/*.md; do
  commits=$(git log --follow --oneline "$file" | wc -l)
  if [ $commits -eq 0 ]; then
    echo "⚠️  No history: $file"
  fi
done
```

---

## 📁 OPERATION LOGGING

### Log Structure:
```
.workspace/departments/infrastructure/git-control-ai/
├── logs/
│   ├── validation_20251012_0200.log
│   ├── validation_20251012_0400.log
│   └── validation_20251012_0600.log
├── git-operations/
│   ├── operations_log.md          # All operations
│   ├── violations_log.md          # Any violations
│   └── history_verification.md    # History checks
└── reports/
    └── GIT_OPERATIONS_REPORT.md   # Final report
```

### Operation Log Format:
```markdown
## [TIMESTAMP] Operation

**Type**: [GIT_MV/CONSOLIDATE/ARCHIVE/UPDATE_REF]
**Agent**: [agent-name]
**Files**: [list]
**Commit**: [hash]
**Status**: [SUCCESS/BLOCKED/CORRECTED]
**Notes**: [any relevant info]
```

---

## 🚨 ESCALATION MATRIX

| Issue | Severity | Action | Escalate To |
|-------|----------|--------|-------------|
| Plain `mv` used | HIGH | Block & correct | Agent directly |
| Protected file modified | CRITICAL | Immediate block | master-orchestrator |
| Commit format wrong | MEDIUM | Reject & guide | Agent directly |
| Code + docs mixed | HIGH | Split & resubmit | Agent directly |
| History lost | CRITICAL | Investigate & restore | master-orchestrator |
| Multiple violations | CRITICAL | Suspend operations | director-enterprise-ceo |

---

## ✅ COMPLETION CRITERIA

Reorganization is COMPLETE when:

1. ✅ All 122 files processed
2. ✅ Final structure matches proposed design
3. ✅ All history verified (sample 15+ files)
4. ✅ Repository integrity confirmed (git fsck)
5. ✅ No files lost (git status clean)
6. ✅ All commits properly formatted
7. ✅ GIT_OPERATIONS_REPORT.md generated
8. ✅ Code references updated (if needed)
9. ✅ Final validation passed
10. ✅ master-orchestrator approval received

---

**🎯 COMMITMENT**: Zero-tolerance for violations
**⚡ AUTHORITY**: EXCLUSIVE Git control
**📝 ACCOUNTABILITY**: Full operation documentation

---

**Protocol Version**: 1.0
**Effective Date**: 2025-10-12
**Authority**: git-control-ai
**Approved By**: master-orchestrator (implicit)
