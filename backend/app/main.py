from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.core.config import settings
from app.api.v1.router import api_router
from app.shared.cache.cache_manager import cache_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 初始化上下文，如缓存连接、AI Client 检查等
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    await cache_manager.initialize()
    
    yield
    
    # Shutdown: 清理资源，如关闭数据库连接、清理本级缓存等
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await cache_manager.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 线上需替换为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip Middleware 配置
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 其他潜在中间件：RateLimit，AuthToken检查 等 (可后续扩展)

# 挂载 API V1 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    """基础健康检查 API"""
    return {"status": "ok"}
