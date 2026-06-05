from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.config.settings import get_settings
from backend.app.routes import alerts, dashboard, health, predict, train
from backend.app.utils.logging import configure_logging
from backend.app.core.limiter import limiter

configure_logging()
settings = get_settings()

app = FastAPI(
    title="MinePredict API",
    description="API FastAPI pour la maintenance prédictive des équipements lourds miniers.",
    version="1.0.0",
)

# =====================
# RATE LIMITING GLOBAL
# =====================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =====================
# MIDDLEWARE
# =====================
# Parse allowed origins from settings (comma-separated for flexibility)
allowed_origins = [
    origin.strip() for origin in settings.allowed_origins.split(",")
]
# Add frontend_url if not already included
if settings.frontend_url not in allowed_origins:
    allowed_origins.insert(0, settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)

    if request.url.path in ["/health", "/metrics"]:
        response.headers["Cache-Control"] = "public, max-age=60"

    elif request.url.path == "/dashboard/stats":
        response.headers["Cache-Control"] = f"public, max-age={settings.cache_ttl_seconds}"

    return response


# =====================
# ROUTES
# =====================
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(predict.router)
app.include_router(train.router)
