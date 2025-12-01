"""
SQLite 自动备份模块
- 支持定时备份
- 限制备份数量，自动清理旧备份
"""
import os
import shutil
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self):
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self._get_db_path()
        self._task = None
        self._last_backup_hash = None  # 用于检测数据库是否变化
    
    def _get_db_path(self) -> Path:
        """从 DATABASE_URL 解析出实际的数据库文件路径"""
        # sqlite+aiosqlite:///./qa_box.db -> ./qa_box.db
        url = settings.DATABASE_URL
        if ":///" in url:
            db_file = url.split(":///")[-1]
            return Path(db_file).resolve()
        return Path("qa_box.db").resolve()
    
    def _get_db_hash(self) -> str | None:
        """获取数据库文件的哈希值（用于检测变化）"""
        if not self.db_path.exists():
            return None
        # 使用文件大小和修改时间作为简单的哈希
        stat = self.db_path.stat()
        return f"{stat.st_size}_{stat.st_mtime}"
    
    def _should_backup(self) -> bool:
        """判断是否需要备份（数据库是否有变化）"""
        current_hash = self._get_db_hash()
        if current_hash is None:
            return False
        
        # 如果是首次备份或数据库有变化，则需要备份
        if self._last_backup_hash is None or self._last_backup_hash != current_hash:
            return True
        
        logger.debug("Database unchanged, skipping backup")
        return False
    
    def create_backup(self, force: bool = False) -> str | None:
        """创建一个数据库备份
        
        Args:
            force: 强制备份，忽略变化检测
        """
        if not self.db_path.exists():
            logger.warning(f"Database file not found: {self.db_path}")
            return None
        
        # 检查是否需要备份
        if not force and not self._should_backup():
            logger.info("Skipping backup: database unchanged")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"qa_box_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            
            # 更新哈希值
            self._last_backup_hash = self._get_db_hash()
            
            self._cleanup_old_backups()
            return str(backup_path)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """清理旧备份，保留最近 N 个"""
        max_backups = settings.BACKUP_MAX_COUNT
        backups = sorted(
            self.backup_dir.glob("qa_box_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backups[max_backups:]:
            try:
                old_backup.unlink()
                logger.info(f"Deleted old backup: {old_backup}")
            except Exception as e:
                logger.error(f"Failed to delete old backup {old_backup}: {e}")
    
    def list_backups(self) -> list[dict]:
        """列出所有备份"""
        backups = sorted(
            self.backup_dir.glob("qa_box_backup_*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return [
            {
                "name": b.name,
                "size": b.stat().st_size,
                "created_at": datetime.fromtimestamp(b.stat().st_mtime).isoformat()
            }
            for b in backups
        ]
    
    async def start_scheduled_backup(self):
        """启动定时备份任务"""
        interval_hours = settings.BACKUP_INTERVAL_HOURS
        if interval_hours <= 0:
            logger.info("Scheduled backup disabled (interval <= 0)")
            return
        
        logger.info(f"Starting scheduled backup every {interval_hours} hours")
        
        async def backup_loop():
            while True:
                await asyncio.sleep(interval_hours * 3600)
                self.create_backup()
        
        self._task = asyncio.create_task(backup_loop())
    
    def stop_scheduled_backup(self):
        """停止定时备份任务"""
        if self._task:
            self._task.cancel()
            self._task = None
            logger.info("Scheduled backup stopped")


# 全局备份管理器实例
backup_manager = BackupManager()
