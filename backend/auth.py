"""
Admin 认证模块
- JWT Token 认证
- 自动续期机制
"""
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_admin_token(username: str) -> dict:
    """创建 Admin JWT Token"""
    expire = datetime.utcnow() + timedelta(days=settings.ADMIN_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": username,
        "type": "admin",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expire.isoformat()
    }


def decode_admin_token(token: str) -> dict | None:
    """解码并验证 Admin Token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "admin":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None


def check_token_needs_refresh(payload: dict) -> bool:
    """检查 Token 是否需要续期"""
    exp = payload.get("exp")
    if not exp:
        return False
    expire_time = datetime.fromtimestamp(exp)
    remaining = expire_time - datetime.utcnow()
    return remaining.days < settings.ADMIN_TOKEN_REFRESH_DAYS


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    验证当前请求的 Admin 身份
    返回: {"username": str, "new_token": str | None}
    如果 Token 即将过期，会返回新 Token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_admin_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的 Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username = payload.get("sub")
    result = {"username": username, "new_token": None}
    
    # 检查是否需要续期
    if check_token_needs_refresh(payload):
        new_token_data = create_admin_token(username)
        result["new_token"] = new_token_data["access_token"]
    
    return result


def verify_admin_credentials(username: str, password: str) -> bool:
    """
    验证管理员凭据
    使用环境变量配置的用户名密码
    """
    if username != settings.ADMIN_USERNAME:
        return False
    # 简单对比密码（生产环境建议使用哈希存储）
    return password == settings.ADMIN_PASSWORD
