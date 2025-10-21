# INDEX-DECISIONS - Architectural & Strategic Decisions

**Generated**: 2025-10-13
**Purpose**: Document key project decisions and their rationale

---

## Platform & Infrastructure Decisions

### Decision: Migration to Railway (Oct 2025)
**Status**: IMPLEMENTED ✅
**Rationale**:
- Better performance than Render
- Simplified deployment process
- Cost-effective for production workload

**Evidence**:
- Commit 1b67f9d3: requirements_production.txt for Railway
- Commit 8ffbebf5: CORS updated for mestocker.com
- `.workspace/cors-https-fix/` documentation

**Impact**:
- Reduced deployment time
- Optimized production dependencies (24 packages)
- Domain integration (mestocker.com)

---

### Decision: PostgreSQL as Primary Database
**Status**: PRODUCTION
**Rationale**:
- ACID compliance needed for e-commerce
- Async support (asyncpg)
- JSON field support
- Strong community support

**Evidence**: `app/database.py`, 34 tables implemented

---

### Decision: FastAPI as Backend Framework
**Status**: PRODUCTION
**Rationale**:
- High performance (async)
- Auto-generated API docs
- Pydantic integration
- Modern Python features

**Evidence**: `app/main.py`, 50+ endpoints

---

## Architecture Decisions

### Decision: Monolithic Backend with Modular Structure
**Status**: PRODUCTION
**Location**: `docs/architecture/`

**Rationale**:
- Simpler deployment for MVP
- Easier debugging
- Single database
- Future microservices migration possible

**Structure**:
```
app/
├── api/v1/          # Versioned API
├── models/          # Database models
├── services/        # Business logic
├── schemas/         # Validation
```

---

### Decision: React + TypeScript Frontend
**Status**: PRODUCTION
**Rationale**:
- Type safety with TypeScript
- Component reusability
- Large ecosystem
- Vite for fast builds

**Evidence**: `frontend/` with Vite 7.1.4

---

### Decision: Multi-Vendor Marketplace Architecture
**Status**: PRODUCTION
**Documentation**: `docs/VENDOR_MANAGEMENT_COMPLETE.md`

**Rationale**:
- Support multiple sellers
- Commission-based revenue model
- Competitive advantage

**Implementation**:
- Vendor model with approval workflow
- Per-vendor product management
- Commission tracking system
- Vendor dashboard

---

## Security Decisions

### Decision: JWT-Based Authentication
**Status**: PRODUCTION
**Documentation**: `docs/security/JWT_ENCRYPTION_SECURITY_STANDARDS.md`

**Rationale**:
- Stateless authentication
- Scalable
- Industry standard
- Mobile-friendly

**Implementation**:
- Python-Jose for JWT
- Bcrypt for password hashing
- Role-based access control

---

### Decision: Separate Admin Login Flow
**Status**: PRODUCTION
**Location**: `frontend/src/pages/AdminLogin.tsx`

**Rationale**:
- Enhanced security
- Different UX requirements
- Separate authentication endpoint
- Protected admin routes

**Critical Protection**: admin@mestocker.com account

---

## Payment Integration Decisions

### Decision: Multiple Payment Gateway Support
**Status**: PRODUCTION
**Documentation**: `docs/guides/integration/PAYMENT_INTEGRATION_COMPLETE_GUIDE.md`

**Gateways Implemented**:
1. **Wompi** (Primary)
   - PSE, cards, Nequi
   - Local Colombian market leader
2. **PayU** (Secondary)
   - Efecty (cash payments)
   - Broader LATAM support

**Rationale**:
- Market coverage
- Payment method diversity
- Risk mitigation (gateway redundancy)

---

## Database Decisions

### Decision: UUID as Primary Keys
**Status**: PRODUCTION
**Format**: String(36)

**Rationale**:
- Distributed system ready
- No sequential ID leakage
- Merge-friendly
- API security (no enumeration)

**Impact**: All 34 tables use UUID PKs

---

### Decision: Alembic for Migrations
**Status**: PRODUCTION
**Documentation**: `scripts/MIGRATION_COMMANDS.md`, `Makefile`

**Rationale**:
- Industry standard for SQLAlchemy
- Multi-environment support
- Rollback capability
- Auto-generation from models

**Tools Created**:
- 30+ Make commands
- Python migration scripts
- Docker integration

---

## Testing Decisions

### Decision: TDD with RED-GREEN-REFACTOR Framework
**Status**: PRODUCTION
**Documentation**: `docs/reports/TDD_SETUP_COMPLETE.md`

**Rationale**:
- Enforce test-first development
- Clear testing phases
- Better code quality
- Pytest marker integration

**Coverage Target**: >75%

---

### Decision: Multi-Layer Testing Strategy
**Status**: PRODUCTION

**Layers**:
1. **Unit Tests** (pytest)
   - Model tests
   - Service tests
   - Schema validation tests

2. **Integration Tests**
   - API endpoint tests
   - Database integration tests
   - Service integration tests

3. **E2E Tests** (Playwright)
   - User flows
   - Critical paths
   - Cross-browser testing

**Documentation**: `docs/reports/testing/2025-Q4/`

---

## Frontend Decisions

### Decision: Zustand for State Management
**Status**: PRODUCTION

**Rationale**:
- Lightweight vs Redux
- Simple API
- TypeScript support
- No boilerplate

---

### Decision: Tailwind CSS for Styling
**Status**: PRODUCTION

**Rationale**:
- Utility-first approach
- Rapid development
- Consistent design
- Small bundle size

---

### Decision: React Router v6
**Status**: PRODUCTION

**Rationale**:
- Latest version features
- Protected routes support
- Nested routing
- Code splitting

---

## Documentation Decisions

### Decision: Organized docs/ Structure
**Status**: IMPLEMENTED ✅
**Commit**: 87fecd74

**Structure**:
```
docs/
├── architecture/
├── guides/
│   ├── setup/
│   ├── features/
│   ├── integration/
├── reports/
│   ├── testing/2025-Q4/
│   ├── implementation/2025-Q4/
│   ├── bugs/2025-Q4/
│   ├── audits/2025-Q4/
│   ├── security/2025-Q4/
│   ├── performance/2025-Q4/
├── executive/
├── api/
```

**Rationale**:
- Professional organization
- Quarterly reporting structure
- Easy navigation
- Clear categorization

---

### Decision: Script Organization
**Status**: IMPLEMENTED ✅

**Structure**:
```
scripts/
├── analysis/
├── testing/
├── validation/
├── debug/
├── database/
├── deployment/
├── maintenance/
├── services/
```

**Rationale**:
- No scripts in root directory
- Category-based organization
- Easy discovery
- Maintainability

---

## Development Workflow Decisions

### Decision: .workspace Agent Protocol
**Status**: ACTIVE
**Documentation**: `.workspace/`

**Rationale**:
- Multi-agent coordination
- File protection protocols
- Escalation procedures
- Prevent breaking changes

**Critical Files**: `.workspace/PROTECTED_FILES.md`

---

### Decision: Semantic Commit Messages
**Status**: ENFORCED

**Format**: `type(scope): description`

**Types**: feat, fix, docs, style, refactor, test, chore, security

**Evidence**: Recent commits follow convention

---

## Deployment Decisions

### Decision: Lightweight Production Dependencies
**Status**: IMPLEMENTED ✅
**File**: `requirements_production.txt`

**Rationale**:
- Faster deployment
- Reduced attack surface
- Lower memory footprint
- Exclude ML/AI libs for now

**Result**: 24 packages (~80MB) vs 50+ packages in dev

---

### Decision: Railway Environment Variables
**Status**: CONFIGURED
**Documentation**: `.workspace/cors-https-fix/RAILWAY_VARIABLES_REQUERIDAS.md`

**Critical Variables**:
- DATABASE_URL
- SECRET_KEY
- CORS_ORIGINS
- ALLOWED_HOSTS

---

## Rejected Decisions (Not Implemented)

### GraphQL API
**Rejected**: Yes
**Reason**: REST API sufficient for MVP, lower complexity

### Redis for Primary Storage
**Rejected**: Yes
**Reason**: PostgreSQL better for relational data, Redis only for caching

### Microservices from Start
**Rejected**: Yes
**Reason**: Over-engineering for MVP, monolith easier to maintain

### NoSQL Database
**Rejected**: Yes
**Reason**: E-commerce needs strong ACID guarantees

---

## Future Decisions (Pending)

### Rate Limiting Strategy
**Status**: PENDING
**Priority**: HIGH
**Timeline**: This month

### Staging Environment
**Status**: PENDING
**Priority**: MEDIUM
**Timeline**: This quarter

### CDN Integration
**Status**: PENDING
**Priority**: LOW
**Timeline**: Next quarter

### Mobile App Framework
**Status**: PENDING
**Priority**: LOW
**Timeline**: Future

---

## Decision Change Log

### 2025-10-13: Railway Migration
- **From**: Render + Vercel
- **To**: Railway + Vercel
- **Reason**: Performance and cost optimization

### 2025-10-12: Security Hardening
- **Change**: P1 security fixes for vendor endpoints
- **Reason**: Security audit findings

### 2025-10-05: Production Deployment
- **Milestone**: First production deployment
- **Platform**: Render (now migrated to Railway)

---

**Last Updated**: 2025-10-13
**Maintained By**: project-librarian
**Review Frequency**: When major decisions are made
