from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .main_router import router
from .config import settings
from .database import engine, Base
from .middleware import LogMiddleware
from .backup import backup_manager
import os

app = FastAPI(
    title="QA Box API",
    description="匿名提问箱后端服务",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-New-Token"],  # 允许前端读取续期 Token
)

# Unified Logging Middleware
app.add_middleware(LogMiddleware)

# Mount static files - 支持子目录
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
    
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR, html=False), name="uploads")
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 启动时创建一次备份（仅在数据库有变化时）
    backup_manager.create_backup(force=False)
    
    # 启动定时备份任务
    await backup_manager.start_scheduled_backup()


@app.on_event("shutdown")
async def shutdown():
    # 停止定时备份
    backup_manager.stop_scheduled_backup()


@app.get("/")
async def root():
    return {"message": "QA Box API is running"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
