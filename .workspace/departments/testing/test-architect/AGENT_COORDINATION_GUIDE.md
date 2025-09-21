# Agent Coordination Guide
*Test Architect - 2025-09-20*

## 🤝 INTER-AGENT COLLABORATION

### 📋 COORDINATION WITH TESTING TEAM

#### TDD Specialist
**Primary Collaboration**: Direct implementation partner
**Handoff Documents**:
- `TEST_IMPLEMENTATION_SPECS.md` - Detailed test specifications
- `SKIPPED_TESTS_ENABLEMENT_PLAN.md` - Week-by-week enablement plan

**Coordination Protocol**:
1. **Daily Standups**: Progress on critical tests (Week 1 focus)
2. **Weekly Reviews**: Coverage metrics and blockers
3. **Immediate Escalation**: Any failing critical tests

**Expected Deliverables from TDD Specialist**:
- Week 1: Authentication, Payment, Order service tests (95% coverage)
- Week 2: Vendor, Product service tests (85% coverage)
- Week 3: Commission, Inventory, Search service tests (85% coverage)
- Week 4: Performance optimization and final validation

#### Code Analysis Expert
**Expected Inputs**:
- Critical function analysis for payment processing
- Security vulnerability assessment for auth system
- Performance bottleneck identification
- Code complexity metrics for testing prioritization

**Information Request**:
```
Please provide:
1. Top 10 most critical functions requiring 100% test coverage
2. Security-sensitive modules requiring enhanced testing
3. Performance-critical paths requiring benchmark tests
4. Code complexity analysis for test prioritization
```

#### Database Testing Specialist
**Collaboration Scope**:
- Database test isolation strategies
- Transaction rollback patterns
- Performance testing for database queries
- Migration testing protocols

**Coordination Points**:
- Database fixture optimization
- Test data management
- Query performance benchmarks
- Schema validation testing

#### API Testing Specialist
**Collaboration Scope**:
- Endpoint test automation
- Request/response validation
- API security testing
- Integration test protocols

**Coordination Points**:
- API test data consistency
- Mock service implementations
- Error handling validation
- Performance benchmarking

### 🏗️ COORDINATION WITH ARCHITECTURE TEAM

#### System Architect AI
**Consultation Required For**:
- Testing architecture decisions
- Performance benchmarks alignment
- Infrastructure testing requirements
- Quality gate definitions

**Information Sharing**:
- Testing strategy alignment with system architecture
- Performance testing requirements
- Infrastructure testing protocols

#### Database Architect AI
**Consultation Required For**:
- Database testing strategies
- Migration testing protocols
- Performance benchmarks for database operations
- Data integrity testing requirements

**Protected Files Coordination**:
- `app/models/user.py` - Test data creation protocols
- `tests/conftest.py` - Fixture modification requests
- Database migration testing strategies

### 🔐 COORDINATION WITH SECURITY TEAM

#### Security Backend AI
**Critical Coordination**:
- Authentication testing protocols
- Security vulnerability testing
- JWT token testing strategies
- Role-based access control testing

**Protected Files Consultation**:
- `app/api/v1/deps/auth.py` - Testing strategy for auth dependencies
- `app/services/auth_service.py` - Security testing requirements

#### Cybersecurity AI
**Collaboration Points**:
- Security test specifications
- Vulnerability testing protocols
- Penetration testing coordination
- Security audit requirements

### ⚙️ COORDINATION WITH BACKEND TEAM

#### Backend Framework AI
**Collaboration Points**:
- Service testing protocols
- Business logic testing strategies
- Error handling testing
- Performance testing requirements

#### API Architect AI
**Coordination Scope**:
- API testing standards
- Endpoint testing protocols
- Integration testing strategies
- API performance benchmarks

### 🎨 COORDINATION WITH FRONTEND TEAM

#### React Specialist AI
**Testing Coordination**:
- Frontend test strategy alignment
- Component testing protocols
- Integration testing with backend
- E2E testing coordination

**Shared Concerns**:
- API contract testing
- Authentication flow testing
- User journey testing
- Performance testing

### ☁️ COORDINATION WITH INFRASTRUCTURE TEAM

#### Cloud Infrastructure AI
**Collaboration Points**:
- Testing environment setup
- CI/CD pipeline testing
- Performance testing infrastructure
- Monitoring and alerting for tests

**Protected Files Consultation**:
- `docker-compose.yml` - Testing environment configuration
- CI/CD pipeline testing strategies

## 📋 SPECIFIC AGENT REQUESTS

### 🔍 TO CODE ANALYSIS EXPERT
**Immediate Request**: Critical Function Analysis
```
Priority: HIGH
Deadline: 2 days

Please analyze and provide:

1. **Payment Processing Functions** (CRITICAL)
   - Most complex payment calculation methods
   - Security-sensitive payment validation functions
   - Error-prone payment state transitions
   - Performance-critical payment processing paths

2. **Authentication Functions** (CRITICAL)
   - JWT token generation/validation complexity
   - Password hashing/verification functions
   - Role-based access control logic
   - Session management critical paths

3. **Order Processing Functions** (HIGH)
   - Order state transition logic
   - Order validation complexity
   - Inventory integration points
   - Commission calculation methods

4. **Database Query Analysis** (HIGH)
   - Most expensive database queries
   - Complex join operations
   - Potential N+1 query issues
   - Index usage optimization opportunities

Deliverable Format:
- Function signature
- Complexity score (1-10)
- Business criticality (1-10)
- Testing priority recommendation
- Specific test scenarios needed
```

### 🗄️ TO DATABASE TESTING SPECIALIST
**Coordination Request**: Test Database Strategy
```
Priority: MEDIUM
Deadline: 1 week

Please coordinate on:

1. **Database Test Isolation**
   - Current transaction rollback strategy
   - Test data contamination risks
   - Fixture optimization opportunities

2. **Performance Testing**
   - Database query benchmarks
   - Connection pool testing
   - Migration performance testing

3. **Data Integrity Testing**
   - Constraint validation testing
   - Relationship integrity testing
   - Migration data consistency testing

Coordination Meeting: Schedule within 2 days
```

### 🔌 TO API TESTING SPECIALIST
**Collaboration Request**: Endpoint Testing Strategy
```
Priority: MEDIUM
Deadline: 1 week

Please collaborate on:

1. **Critical Endpoint Prioritization**
   - Payment endpoints testing strategy
   - Authentication endpoints comprehensive testing
   - Order processing endpoints validation

2. **Mock Service Strategy**
   - External service mocking patterns
   - Webhook testing protocols
   - Error simulation strategies

3. **Integration Testing**
   - Service-to-service communication testing
   - API contract testing
   - Performance benchmarking

Deliverable: Joint testing protocol document
```

## 🚨 ESCALATION PROTOCOLS

### Critical Issues (Immediate Escalation)
- Test failures blocking deployment
- Security vulnerabilities in testing
- Performance regressions
- Database corruption in tests

**Escalation Path**:
1. **Immediate**: Team Testing Orchestrator
2. **1 hour**: Development Coordinator
3. **4 hours**: Master Orchestrator

### Non-Critical Issues (Standard Process)
- Test coverage gaps
- Performance optimization opportunities
- Test maintenance requests

**Escalation Path**:
1. **24 hours**: Relevant specialist agent
2. **3 days**: Team Testing Orchestrator
3. **1 week**: Development Coordinator

## 📅 MEETING SCHEDULE

### Daily Testing Standup (15 minutes)
**Participants**: Test Architect, TDD Specialist, Testing Team
**Time**: 9:00 AM
**Agenda**: Progress, blockers, daily priorities

### Weekly Testing Review (45 minutes)
**Participants**: All testing agents + relevant architects
**Time**: Friday 2:00 PM
**Agenda**: Coverage metrics, quality gates, next week planning

### Monthly Testing Strategy Review (2 hours)
**Participants**: Testing team + architecture team + stakeholders
**Time**: Last Friday of month
**Agenda**: Strategy updates, tool evaluation, process improvements

## 📊 REPORTING AND METRICS

### Daily Reports
- Tests enabled/disabled
- Coverage percentage changes
- Critical test failures
- Performance regressions

### Weekly Reports
- Coverage trend analysis
- Test execution performance
- Quality gate compliance
- Agent coordination effectiveness

### Monthly Reports
- Testing strategy effectiveness
- Agent collaboration metrics
- Process improvement recommendations
- Tool and framework evaluation

## 🔗 COMMUNICATION CHANNELS

### Immediate Communication
- **Critical Issues**: Direct agent mention in commit messages
- **Urgent Coordination**: `.workspace/communications/urgent/`
- **Blocker Resolution**: `.workspace/communications/blockers/`

### Standard Communication
- **Progress Updates**: `.workspace/communications/daily/`
- **Coordination Requests**: `.workspace/communications/requests/`
- **Documentation Updates**: `.workspace/communications/updates/`

---

## 🎯 SUCCESS METRICS FOR COORDINATION

### Agent Collaboration Effectiveness
- Response time to requests: <4 hours
- Coordination meeting attendance: 95%+
- Deliverable quality scores: 90%+
- Cross-agent dependency resolution: <24 hours

### Testing Strategy Implementation
- Coverage target achievement: 85%+
- Test enablement schedule adherence: 95%+
- Quality gate compliance: 100%
- Performance target achievement: 95%+

---

*This coordination guide ensures effective collaboration between the Test Architect and all relevant agents to achieve comprehensive testing coverage and quality assurance for MeStore.*