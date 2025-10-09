# Environment Variables Checklist - MeStore Orders System

## 🔐 Required Environment Variables

### Database Configuration
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `DATABASE_POOL_SIZE` - Connection pool size (default: 20)
- [ ] `DATABASE_MAX_OVERFLOW` - Max overflow connections (default: 10)

### JWT Authentication
- [ ] `SECRET_KEY` - JWT secret key (MUST be unique in production)
- [ ] `ALGORITHM` - JWT algorithm (default: HS256)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

### Security
- [ ] `ENVIRONMENT` - Set to "production" for production deployment
- [ ] `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- [ ] `RATE_LIMIT_ENABLED` - Enable rate limiting (default: true)

### Optional Services
- [ ] `REDIS_URL` - Redis connection string (optional, for caching)
- [ ] `SENTRY_DSN` - Sentry error tracking (optional)

## 🚨 Security Verification

### No Hardcoded Secrets
- [ ] No hardcoded passwords in code
- [ ] No API keys in source files
- [ ] No database credentials in code
- [ ] All secrets in environment variables

### Production Security
- [ ] ENVIRONMENT set to "production"
- [ ] Unique SECRET_KEY generated
- [ ] CORS properly configured
- [ ] Rate limiting enabled

## ✅ Deployment Status
- **Created**: 2025-10-09
- **Status**: PENDING VERIFICATION
- **Phase**: FASE 7.1
