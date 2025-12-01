"""
上传文件工具模块
- 按周分文件夹存储
"""
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from .config import settings


def get_week_folder() -> str:
    """
    获取当前周的文件夹名称
    格式: YYYY-MM-DD (该周周一的日期)
    """
    today = datetime.now().date()
    # 计算本周一的日期 (weekday(): Monday=0, Sunday=6)
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y-%m-%d")


def get_upload_path(filename: str) -> tuple[str, str]:
    """
    获取上传文件的存储路径
    返回: (完整文件路径, 相对URL路径)
    """
    # 获取文件扩展名
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    
    # 生成唯一文件名
    new_filename = f"{uuid.uuid4()}.{ext}"
    
    # 获取周文件夹
    week_folder = get_week_folder()
    
    # 创建目录
    folder_path = Path(settings.UPLOAD_DIR) / week_folder
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # 完整路径
    file_path = folder_path / new_filename
    
    # URL 路径
    url_path = f"/uploads/{week_folder}/{new_filename}"
    
    return str(file_path), url_path


def cleanup_empty_folders():
    """清理空的上传文件夹"""
    upload_dir = Path(settings.UPLOAD_DIR)
    for folder in upload_dir.iterdir():
        if folder.is_dir() and not any(folder.iterdir()):
            try:
                folder.rmdir()
            except OSError:
                pass
