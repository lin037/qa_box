from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import shutil
import jwt
import os
from pathlib import Path
from datetime import datetime, timedelta
from . import models, schemas, database, config
from .auth import get_current_admin, verify_admin_credentials, create_admin_token
from .upload_utils import get_upload_path

router = APIRouter()

# ============================================
# 公共工具函数
# ============================================
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# ============================================
# 公共接口 (无需鉴权)
# ============================================
@router.post("/upload", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """上传图片 - 按周分文件夹存储
    
    普通用户限制: 10MB/张
    Admin用户: 无限制
    """
    # Check if user is admin
    is_admin = False
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
            if payload.get("role") == "admin":
                is_admin = True
        except jwt.PyJWTError:
            pass
    
    # File size validation for non-admin users
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    if not is_admin:
        # Read file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件大小超过限制（最大10MB），当前: {file_size / 1024 / 1024:.1f}MB"
            )
    
    file_path, url_path = get_upload_path(file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"url": url_path}


@router.post("/questions", response_model=schemas.Token)
async def create_question(question: schemas.QuestionCreate, db: AsyncSession = Depends(database.get_db)):
    """提交新问题"""
    new_question = models.Question(**question.model_dump())
    db.add(new_question)
    await db.commit()
    await db.refresh(new_question)
    
    # Generate JWT for the user (to serve as ownership proof for revocation)
    token = create_jwt_token({"sub": str(new_question.id), "type": "asker"})
    
    return {"access_token": token, "token_type": "bearer", "question_id": new_question.id}


@router.get("/questions/{question_id}", response_model=schemas.QuestionOut)
async def get_question(question_id: str, db: AsyncSession = Depends(database.get_db)):
    """获取单个问题详情"""
    result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.post("/questions/revoke")
async def revoke_question(revoke_data: schemas.RevokeRequest, db: AsyncSession = Depends(database.get_db)):
    """撤回问题 (需要提问时返回的 token)"""
    payload = decode_jwt_token(revoke_data.token)
    if not payload or payload.get("type") != "asker":
        raise HTTPException(status_code=401, detail="Invalid token")
        
    question_id = payload.get("sub")
    result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = result.scalars().first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
         
    if question.is_answered:
        raise HTTPException(status_code=400, detail="Cannot revoke answered question")

    await db.delete(question)
    await db.commit()
    return {"message": "Question revoked successfully"}


@router.get("/public/questions", response_model=List[schemas.QuestionOut])
async def list_public_questions(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(database.get_db)):
    """获取公开的已回答问题列表"""
    result = await db.execute(
        select(models.Question)
        .where(models.Question.is_answered == True)
        .where(models.Question.is_public == True)
        .order_by(models.Question.answered_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/questions/batch", response_model=List[schemas.QuestionOut])
async def get_questions_batch(question_ids: List[str], db: AsyncSession = Depends(database.get_db)):
    """批量获取问题状态 (用于前端刷新我的问题列表)
    
    注意: 已删除的问题不会在结果中返回，前端需要处理这种情况
    """
    if len(question_ids) > 100:
        raise HTTPException(status_code=400, detail="Too many IDs")
         
    result = await db.execute(
        select(models.Question)
        .where(models.Question.id.in_(question_ids))
        .order_by(models.Question.created_at.desc())
    )
    # 返回找到的问题，不存在的ID会被自动忽略
    return result.scalars().all()


# ============================================
# Admin 登录接口 (无需鉴权)
# ============================================
ADMIN_PREFIX = config.settings.ADMIN_ROUTE_PREFIX


@router.post(f"{ADMIN_PREFIX}/login")
async def admin_login(credentials: schemas.AdminLogin):
    """管理员登录"""
    if not verify_admin_credentials(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    token_data = create_admin_token(credentials.username)
    return token_data


@router.post(f"{ADMIN_PREFIX}/verify")
async def verify_token(admin: dict = Depends(get_current_admin)):
    """验证 Token 有效性，并返回续期后的新 Token (如果需要)"""
    return {
        "valid": True,
        "username": admin["username"],
        "new_token": admin.get("new_token")
    }


# ============================================
# Admin 管理接口 (需要鉴权)
# ============================================
@router.get(f"{ADMIN_PREFIX}/questions", response_model=List[schemas.QuestionOut])
async def admin_list_questions(
    skip: int = 0, 
    limit: int = 100, 
    response: Response = None,
    db: AsyncSession = Depends(database.get_db),
    admin: dict = Depends(get_current_admin)
):
    """[Admin] 获取所有问题列表"""
    # 如果有新 Token，通过响应头返回
    if admin.get("new_token"):
        response.headers["X-New-Token"] = admin["new_token"]
    
    result = await db.execute(
        select(models.Question)
        .order_by(models.Question.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.put(f"{ADMIN_PREFIX}/questions/{{question_id}}")
async def admin_update_question(
    question_id: str, 
    update_data: schemas.QuestionUpdate, 
    response: Response = None,
    db: AsyncSession = Depends(database.get_db),
    admin: dict = Depends(get_current_admin)
):
    """[Admin] 更新问题状态"""
    if admin.get("new_token"):
        response.headers["X-New-Token"] = admin["new_token"]
    
    result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if update_data.is_public is not None:
        question.is_public = update_data.is_public
    if update_data.is_answered is not None:
        question.is_answered = update_data.is_answered
        
    await db.commit()
    await db.refresh(question)
    return question


@router.post(f"{ADMIN_PREFIX}/questions/{{question_id}}/answer")
async def admin_answer_question(
    question_id: str, 
    answer: schemas.AnswerCreate, 
    response: Response = None,
    db: AsyncSession = Depends(database.get_db),
    admin: dict = Depends(get_current_admin)
):
    """[Admin] 回答问题"""
    if admin.get("new_token"):
        response.headers["X-New-Token"] = admin["new_token"]
    
    result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    question.answer_content = answer.answer_content
    question.answer_images = answer.answer_images
    question.is_answered = True
    question.is_public = answer.is_public
    question.answered_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(question)
    return question


@router.delete(f"{ADMIN_PREFIX}/questions/{{question_id}}")
async def admin_delete_question(
    question_id: str,
    response: Response = None,
    db: AsyncSession = Depends(database.get_db),
    admin: dict = Depends(get_current_admin)
):
    """[Admin] 删除问题，同时删除关联的图片文件"""
    if admin.get("new_token"):
        response.headers["X-New-Token"] = admin["new_token"]
    
    result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # 收集所有需要删除的图片URL
    image_urls = []
    if question.images:
        image_urls.extend(question.images)
    if question.answer_images:
        image_urls.extend(question.answer_images)
    
    # 删除本地图片文件
    deleted_count = 0
    for url in image_urls:
        # URL格式: /uploads/YYYY-MM-DD/filename.ext
        if url.startswith("/uploads/"):
            # 构建完整文件路径
            relative_path = url.lstrip("/")  # 去掉开头的 /
            file_path = Path(config.settings.UPLOAD_DIR).parent / relative_path
            
            # 删除文件
            try:
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
                    deleted_count += 1
            except Exception as e:
                # 记录错误但不阻止删除操作
                print(f"Failed to delete image file {file_path}: {e}")
    
    # 删除数据库记录
    await db.delete(question)
    await db.commit()
    
    return {
        "message": "Question deleted successfully",
        "deleted_images": deleted_count
    }
