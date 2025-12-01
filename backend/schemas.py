from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    content: str
    images: List[str] = []

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: str
    created_at: datetime
    is_answered: bool
    is_public: bool
    answer_content: Optional[str] = None
    answer_images: List[str] = []
    answered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnswerCreate(BaseModel):
    answer_content: str
    answer_images: List[str] = []
    is_public: bool = True

class QuestionUpdate(BaseModel):
    is_public: Optional[bool] = None
    is_answered: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    question_id: str

class RevokeRequest(BaseModel):
    token: str

# Admin 登录相关
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str
