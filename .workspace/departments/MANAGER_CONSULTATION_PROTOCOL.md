# 🏢 MANAGER CONSULTATION PROTOCOL
**MeStore Project - Department Team Coordination**
**Version: 1.0.0**
**Date: September 14, 2025**
**Status: ACTIVE**

---

## 📋 OVERVIEW

This protocol establishes mandatory consultation procedures for all agents working on the MeStore project. Following today's system recovery incident, these protocols ensure coordinated development and prevent unauthorized changes that could break production systems.

## 🎯 CORE PRINCIPLES

### 1. **MANDATORY CONSULTATION**
- All agents MUST consult the enterprise-project-manager before making any system changes
- No agent may modify core system components without manager approval
- All changes must be logged and tracked through the proper channels

### 2. **PROJECT CONTEXT REQUIREMENT**
- All agents MUST review `/home/admin-jairo/MeStore/.workspace/departments/PROJECT_CONTEXT.md` before starting work
- Agents must understand current system state before making modifications
- When in doubt about system architecture, consult the project manager immediately

### 3. **CHANGE AUTHORIZATION MATRIX**

#### ✅ **LOW-RISK CHANGES** (Agent Independent):
- Adding new unit tests
- Updating documentation
- Code formatting and linting
- Adding new API endpoints (non-breaking)
- Frontend UI improvements

#### ⚠️ **MEDIUM-RISK CHANGES** (Manager Consultation Required):
- Database schema modifications
- Authentication system changes
- Security-related modifications
- Environment configuration updates
- Third-party service integrations

#### 🚫 **HIGH-RISK CHANGES** (Manager Authorization Required):
- Database type changes (PostgreSQL ↔ SQLite)
- Core security component modifications
- Production environment changes
- User model relationship changes
- Authentication flow modifications

## 📞 CONSULTATION PROCEDURES

### Step 1: Initial Assessment
1. Review PROJECT_CONTEXT.md for current system state
2. Identify change risk level using the matrix above
3. Document proposed changes in detail

### Step 2: Manager Consultation (Medium/High Risk)
```
I need to consult with the enterprise-project-manager about [specific change].

Current understanding:
- System component: [component name]
- Proposed change: [detailed description]
- Risk assessment: [Low/Medium/High]
- Potential impact: [description]
- Dependencies: [list any dependencies]

Questions for manager:
- [specific questions about the change]
- [concerns about system impact]
```

### Step 3: Authorization Process
- **Low-risk**: Proceed with implementation
- **Medium-risk**: Wait for manager guidance before proceeding
- **High-risk**: Implement ONLY after explicit manager authorization

### Step 4: Change Logging
All changes must be logged in `/home/admin-jairo/MeStore/.workspace/departments/team/TEAM_CHANGES_LOG.md`

## 🚨 EMERGENCY PROTOCOLS

### System Down Scenarios:
1. **STOP** - Do not attempt fixes without manager consultation
2. **ASSESS** - Document the issue and current system state
3. **CONSULT** - Contact enterprise-project-manager immediately
4. **COORDINATE** - Follow manager-directed recovery procedures

### Rollback Procedures:
- Manager must authorize all system rollbacks
- Document rollback reason and scope
- Verify system functionality after rollback
- Update team on rollback completion

## 📊 COMPLIANCE MONITORING

### Weekly Reviews:
- Manager reviews all changes made during the week
- Compliance assessment for protocol adherence
- Team feedback on protocol effectiveness

### Violation Consequences:
- **First Violation**: Warning and protocol re-training
- **Second Violation**: Temporary restricted access
- **Third Violation**: Project removal consideration

## 🔄 PROTOCOL UPDATES

This protocol will be reviewed and updated:
- After any major system incident
- Monthly during team retrospectives
- When new agents join the project
- As system architecture evolves

## 📚 REQUIRED READING

All agents must be familiar with:
1. **PROJECT_CONTEXT.md** - Current system state and architecture
2. **TEAM_COORDINATION_PROTOCOL.md** - General team coordination rules
3. **TEAM_CHANGES_LOG.md** - Change tracking and history

## 🎯 SUCCESS METRICS

Protocol success will be measured by:
- Zero unauthorized system changes
- 100% compliance with consultation requirements
- Reduced system incidents and rollbacks
- Improved team coordination and communication

## 📞 ESCALATION CONTACT

**Primary:** enterprise-project-manager agent
**Secondary:** User (project owner)
**Emergency:** Immediate user notification for system-down scenarios

---

**⚠️ CRITICAL REMINDER:** The system breakdown that occurred today was caused by agents making unauthorized changes to core system components. This protocol is mandatory to prevent future incidents and maintain system stability.

**✅ COMPLIANCE REQUIRED:** All agents working on this project are required to follow this protocol without exception.

---

*Last Updated: September 14, 2025*
*Next Review: October 14, 2025*