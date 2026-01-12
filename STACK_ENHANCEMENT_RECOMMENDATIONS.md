# 🚀 PrimeHaul OS - Stack Enhancement Recommendations

**Review Date:** January 2025  
**Reviewer:** AI Code Assistant  
**Current Stack:** FastAPI + PostgreSQL + OpenAI Vision + Stripe

---

## 📊 Executive Summary

Your stack is **solid and production-ready** with good security foundations. However, there are several **high-impact enhancements** that will improve security, performance, maintainability, and scalability as you grow.

**Priority Levels:**
- 🔴 **Critical** - Security/Reliability issues (fix immediately)
- 🟡 **High** - Performance/UX improvements (fix this month)
- 🟢 **Medium** - Code quality/maintainability (fix this quarter)
- 🔵 **Low** - Nice-to-have optimizations (future)

---

## 🔴 CRITICAL: Security Enhancements

### 1. **CORS Configuration** (Security Risk)
**Current:** `allow_origins=["*"]` - Allows any origin  
**Risk:** CSRF attacks, data leakage  
**Fix:**
```python
# In main.py, replace CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://primehaul.co.uk",
        "https://www.primehaul.co.uk",
        "https://app.primehaul.co.uk",
        # Add staging URL if needed
        "http://localhost:8000" if os.getenv("ENV") == "development" else None
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. **Rate Limiting** (Missing)
**Risk:** API abuse, DDoS, cost overruns (OpenAI API)  
**Recommendation:** Add `slowapi` or `fastapi-limiter`
```python
# Add to requirements.txt:
# slowapi==0.1.9

# In main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to expensive endpoints:
@app.post("/api/analyze-photos")
@limiter.limit("10/minute")  # Limit AI calls
async def analyze_photos(...):
    ...
```

### 3. **Input Validation with Pydantic** (Missing)
**Current:** Using `Form()` directly without validation  
**Risk:** Invalid data, injection attacks  
**Recommendation:** Create Pydantic models for all request bodies
```python
# Create app/schemas.py:
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional

class CompanySignupRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

# Use in endpoints:
@app.post("/auth/signup")
async def signup(data: CompanySignupRequest):
    ...
```

### 4. **JWT Token Refresh** (Missing)
**Current:** 24-hour tokens (too long)  
**Risk:** Stolen tokens remain valid too long  
**Recommendation:** Short-lived access tokens (15 min) + refresh tokens
```python
# In auth.py:
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_refresh_token(user_id: str, company_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "company_id": company_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Add refresh endpoint:
@app.post("/auth/refresh")
async def refresh_token(refresh_token: str = Cookie(...)):
    ...
```

### 5. **Trusted Host Middleware** (Commented Out)
**Current:** TrustedHostMiddleware is commented  
**Risk:** Host header injection  
**Fix:** Uncomment and configure:
```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "primehaul.co.uk",
        "*.primehaul.co.uk",
        "localhost",
        "127.0.0.1"
    ]
)
```

### 6. **File Upload Security** (Partial)
**Current:** Basic file type/size checks  
**Enhancement:** Add virus scanning, content validation
```python
# Add to requirements.txt:
# python-magic==0.4.27  # For MIME type detection

# Enhanced validation:
import magic

def validate_image_file(file: UploadFile) -> bool:
    # Check extension
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return False
    
    # Read first bytes to verify actual file type
    content = await file.read()
    await file.seek(0)  # Reset for later use
    
    mime = magic.from_buffer(content, mime=True)
    if mime not in ['image/jpeg', 'image/png', 'image/webp']:
        return False
    
    # Check file size (already done, but ensure)
    if len(content) > 10 * 1024 * 1024:  # 10MB
        return False
    
    return True
```

---

## 🟡 HIGH: Performance & Scalability

### 7. **Caching Layer** (Missing)
**Impact:** Reduce database load, faster responses  
**Recommendation:** Add Redis for caching
```python
# Add to requirements.txt:
# redis==5.0.1
# aioredis==2.0.1

# Create app/cache.py:
import redis
import json
from typing import Optional

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def cache_key(prefix: str, *args) -> str:
    return f"{prefix}:{':'.join(str(a) for a in args)}"

async def get_cached_company(slug: str) -> Optional[dict]:
    key = cache_key("company", slug)
    data = redis_client.get(key)
    return json.loads(data) if data else None

async def cache_company(slug: str, company_data: dict, ttl: int = 3600):
    key = cache_key("company", slug)
    redis_client.setex(key, ttl, json.dumps(company_data))

# Use in middleware:
company_data = await get_cached_company(company_slug)
if not company_data:
    # Fetch from DB
    company_data = {...}
    await cache_company(company_slug, company_data)
```

**Cache Strategy:**
- Company data: 1 hour TTL
- Pricing configs: 30 minutes TTL
- Job lists: 5 minutes TTL
- AI analysis results: Never cache (always fresh)

### 8. **Database Connection Pooling** (Basic)
**Current:** `pool_size=10, max_overflow=20`  
**Enhancement:** Optimize based on load
```python
# In database.py:
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,  # Increase for production
    max_overflow=40,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,
    echo=False,
)
```

### 9. **Async File Operations** (Partial)
**Current:** Mix of sync/async file operations  
**Enhancement:** Use `aiofiles` consistently
```python
# Already using aiofiles, but ensure all file ops are async:
async def save_uploaded_file(file: UploadFile, path: Path) -> str:
    async with aiofiles.open(path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    return str(path)
```

### 10. **CDN for Static Assets** (Missing)
**Current:** Serving static files from FastAPI  
**Impact:** Slow load times, server load  
**Recommendation:** Use CloudFlare/CDN for:
- CSS files
- JavaScript files
- Images/logos
- Uploaded photos (after processing)

### 11. **Database Indexes** (Review Needed)
**Check:** Ensure all foreign keys and frequently queried columns are indexed
```python
# In models.py, verify indexes exist on:
# - Company.slug (✅ already indexed)
# - User.email (✅ already indexed)
# - User.company_id (✅ already indexed)
# - Job.company_id (check if indexed)
# - Job.token (check if indexed)
# - Job.created_at (for sorting)

# Add if missing:
class Job(Base):
    ...
    __table_args__ = (
        Index('idx_job_company_created', 'company_id', 'created_at'),
        Index('idx_job_token', 'token'),
    )
```

### 12. **Background Tasks** (Missing)
**Current:** AI analysis happens synchronously  
**Impact:** Slow response times, timeout risks  
**Recommendation:** Use Celery or FastAPI BackgroundTasks
```python
# Option 1: FastAPI BackgroundTasks (simple)
from fastapi import BackgroundTasks

@app.post("/api/upload-photos")
async def upload_photos(
    files: List[UploadFile],
    background_tasks: BackgroundTasks
):
    # Save files immediately
    saved_paths = await save_files(files)
    
    # Queue AI analysis in background
    background_tasks.add_task(analyze_photos_async, saved_paths, job_id)
    
    return {"status": "uploaded", "analyzing": True}

# Option 2: Celery (for production scale)
# Better for heavy workloads, retries, monitoring
```

---

## 🟢 MEDIUM: Code Quality & Maintainability

### 13. **Split Large main.py** (3600+ lines)
**Current:** Single monolithic file  
**Impact:** Hard to maintain, test, and collaborate  
**Recommendation:** Split into routers
```
app/
├── main.py (100 lines - app setup only)
├── routers/
│   ├── __init__.py
│   ├── auth.py (login, signup, logout)
│   ├── companies.py (company management)
│   ├── jobs.py (job/quotes endpoints)
│   ├── photos.py (photo upload/analysis)
│   ├── admin.py (admin dashboard)
│   ├── billing.py (Stripe endpoints)
│   └── marketplace.py (marketplace endpoints)
├── api/
│   └── v1/
│       └── __init__.py
└── ...
```

**Example:**
```python
# app/routers/jobs.py
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/")
async def list_jobs(current_user: User = Depends(get_current_user)):
    ...

# app/main.py
from app.routers import auth, jobs, companies, photos, admin, billing, marketplace

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(companies.router)
# ... etc
```

### 14. **API Documentation** (Missing)
**Current:** No OpenAPI docs visible  
**Enhancement:** FastAPI auto-generates, but enhance with descriptions
```python
@app.post(
    "/api/analyze-photos",
    response_model=PhotoAnalysisResponse,
    summary="Analyze photos with AI",
    description="Upload photos of rooms and get AI-generated inventory list",
    responses={
        200: {"description": "Analysis complete"},
        400: {"description": "Invalid file format"},
        429: {"description": "Rate limit exceeded"},
    }
)
async def analyze_photos(...):
    ...
```

**Access:** `/docs` (Swagger UI) and `/redoc` (ReDoc)

### 15. **Type Hints** (Partial)
**Current:** Some functions missing type hints  
**Enhancement:** Add comprehensive type hints
```python
# Use mypy for type checking:
# pip install mypy
# mypy app/

# Example:
from typing import List, Optional, Dict, Any

async def process_job(
    job_id: uuid.UUID,
    company_id: uuid.UUID,
    db: Session
) -> Dict[str, Any]:
    ...
```

### 16. **Error Handling** (Basic)
**Current:** Basic try/except blocks  
**Enhancement:** Centralized error handling
```python
# Create app/exceptions.py:
class PrimeHaulException(Exception):
    status_code: int
    detail: str

class CompanyNotFound(PrimeHaulException):
    status_code = 404
    detail = "Company not found"

class SubscriptionExpired(PrimeHaulException):
    status_code = 403
    detail = "Subscription expired"

# In main.py:
@app.exception_handler(PrimeHaulException)
async def primehaul_exception_handler(request: Request, exc: PrimeHaulException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

### 17. **Logging Enhancement** (Basic)
**Current:** Basic logging  
**Enhancement:** Structured logging with context
```python
# Use structlog or python-json-logger:
# pip install structlog

import structlog

logger = structlog.get_logger()

# Add request ID tracking:
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Use in endpoints:
logger.info(
    "photo_uploaded",
    request_id=request.state.request_id,
    company_id=str(company.id),
    file_count=len(files),
    file_size_mb=total_size / 1024 / 1024
)
```

---

## 🔵 LOW: Monitoring & DevOps

### 18. **Health Check Endpoint** (Missing)
**Recommendation:**
```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database
        db.execute(text("SELECT 1"))
        
        # Check Redis (if added)
        # redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

### 19. **Error Tracking** (Missing)
**Recommendation:** Add Sentry
```python
# Add to requirements.txt:
# sentry-sdk[fastapi]==1.40.0

# In main.py:
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    environment=os.getenv("ENV", "production"),
)
```

### 20. **Testing Framework** (Missing)
**Recommendation:** Add pytest
```python
# Add to requirements.txt:
# pytest==7.4.3
# pytest-asyncio==0.21.1
# httpx==0.25.2  # For testing FastAPI

# Create tests/test_auth.py:
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup():
    response = client.post("/auth/signup", json={
        "company_name": "Test Co",
        "email": "test@example.com",
        "password": "Test1234!"
    })
    assert response.status_code == 200

# Run: pytest tests/
```

### 21. **Docker Containerization** (Missing)
**Recommendation:** Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/primehaul
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=primehaul
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 22. **CI/CD Pipeline** (Missing)
**Recommendation:** GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - run: mypy app/
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          # Deploy commands
```

### 23. **Database Backups** (Missing Strategy)
**Recommendation:**
- Automated daily backups (pg_dump)
- Store in S3/cloud storage
- Test restore process monthly
- Keep 30 days of backups

### 24. **Dependency Updates** (Review)
**Current:** Some packages may have updates  
**Recommendation:** Regular updates
```bash
# Check for outdated packages:
pip list --outdated

# Update safely:
pip install --upgrade fastapi uvicorn sqlalchemy

# Use pip-tools for dependency pinning:
# pip install pip-tools
# pip-compile requirements.in
```

---

## 📋 Implementation Priority

### **Week 1 (Critical Security):**
1. ✅ Fix CORS configuration
2. ✅ Add rate limiting
3. ✅ Add input validation (Pydantic)
4. ✅ Enable TrustedHostMiddleware

### **Week 2 (Performance):**
5. ✅ Add Redis caching
6. ✅ Optimize database connection pool
7. ✅ Add background tasks for AI analysis

### **Month 1 (Code Quality):**
8. ✅ Split main.py into routers
9. ✅ Add comprehensive error handling
10. ✅ Enhance logging
11. ✅ Add health check endpoint

### **Month 2 (DevOps):**
12. ✅ Add Docker containerization
13. ✅ Set up CI/CD pipeline
14. ✅ Add Sentry error tracking
15. ✅ Create test suite

---

## 🎯 Quick Wins (Do Today)

1. **Fix CORS** (5 minutes) - Replace `["*"]` with specific origins
2. **Add Health Check** (10 minutes) - Simple `/health` endpoint
3. **Enable TrustedHostMiddleware** (2 minutes) - Uncomment and configure
4. **Add Rate Limiting** (15 minutes) - Install slowapi, add to AI endpoints
5. **Update Dependencies** (10 minutes) - Check for security updates

---

## 📚 Additional Resources

- **FastAPI Best Practices:** https://fastapi.tiangolo.com/tutorial/
- **Security Checklist:** https://owasp.org/www-project-top-ten/
- **PostgreSQL Performance:** https://www.postgresql.org/docs/current/performance-tips.html
- **Redis Caching Patterns:** https://redis.io/docs/manual/patterns/

---

## ✅ Summary

Your stack is **production-ready** but needs these enhancements for **scale and security**:

**Must Have (Now):**
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Input validation

**Should Have (This Month):**
- ✅ Caching layer
- ✅ Code organization (routers)
- ✅ Error tracking

**Nice to Have (This Quarter):**
- ✅ Docker
- ✅ CI/CD
- ✅ Comprehensive testing

**Estimated Impact:**
- **Security:** 🔴 → 🟢 (Critical fixes)
- **Performance:** 🟡 → 🟢 (+50% faster with caching)
- **Maintainability:** 🟡 → 🟢 (Much easier with routers)
- **Reliability:** 🟡 → 🟢 (Better error handling)

---

**Questions or need help implementing any of these? Let me know!** 🚀
