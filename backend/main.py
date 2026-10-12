from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import mongodb, redis as redis_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to databases on startup, disconnect on shutdown."""
    await mongodb.connect()
    await redis_db.connect()
    yield
    await mongodb.disconnect()
    await redis_db.disconnect()


app = FastAPI(
    title="FocusMirror API",
    description="Real-time cognitive load and attention monitoring system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — Member 3's frontend (Next.js) runs on localhost:3000 in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routers — imported here, implemented in Steps 2–6 ────────────────────
# These are stubbed as empty routers now so the app starts cleanly.
# We'll fill them in each subsequent step.

from api import auth, sessions, focus, users, preferences, privacy, dl

app.include_router(auth.router,        prefix="/api/auth",        tags=["Auth"])
app.include_router(sessions.router,    prefix="/api/session",     tags=["Sessions"])
app.include_router(focus.router,       prefix="/api/focus",       tags=["Focus"])
app.include_router(users.router,       prefix="/api/user",        tags=["Users"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["Preferences"])
app.include_router(privacy.router,     prefix="/api/privacy",     tags=["Privacy"])
app.include_router(dl.router,          prefix="/api/dl",          tags=["DL Pipeline"])


# ─── Health check ─────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "focusmirror-backend"}