"""Agent Platform - メインエントリポイント."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_platform.api.routes import a2a, agents, chat, personal_agents, user_settings
from agent_platform.core.config import settings
from agent_platform.db.models import Base
from agent_platform.db.session import engine
from agent_platform.tools import register_default_tools

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    logger.info("Registering default tools...")
    register_default_tools()
    logger.info("Tools registered successfully")

    yield

    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title="Agent Platform API",
    description="マルチユーザー対応AIエージェントプラットフォーム",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(personal_agents.router, prefix="/api/personal-agents", tags=["personal-agents"])
app.include_router(user_settings.router, prefix="/api/user", tags=["user-settings"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(a2a.router, prefix="/a2a", tags=["a2a"])


@app.get("/")
async def root() -> dict[str, str]:
    """ルートエンドポイント."""
    return {"message": "Agent Platform API", "version": "0.1.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """ヘルスチェックエンドポイント."""
    return {"status": "healthy"}


def main() -> None:
    """開発サーバー起動."""
    import uvicorn

    uvicorn.run(
        "agent_platform.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
