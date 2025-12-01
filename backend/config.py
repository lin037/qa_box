import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL: str = "sqlite+aiosqlite:///./qa_box.db"
    SECRET_KEY: str = "your-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days for "session"
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    
    # Admin 配置
    ADMIN_ROUTE_PREFIX: str = "/console-x7k9m"  # 不易猜测的管理路由前缀
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-this-password"  # 生产环境务必修改
    ADMIN_TOKEN_EXPIRE_DAYS: int = 7  # Admin Token 过期天数
    ADMIN_TOKEN_REFRESH_DAYS: int = 1  # 剩余多少天时自动续期
    
    # 备份配置
    BACKUP_DIR: str = os.path.join(BASE_DIR, "backups")
    BACKUP_INTERVAL_HOURS: int = 24  # 自动备份间隔(小时)，0表示禁用
    BACKUP_MAX_COUNT: int = 7  # 最多保留备份数量
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 18000
    FRONTEND_PORT: int = 13000
    WORKERS: int = 2  # Gunicorn workers
    
    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:13000,http://127.0.0.1:13000"
    
    class Config:
        env_file = ".env"
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.BACKUP_DIR, exist_ok=True)
