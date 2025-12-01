import uuid
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.types import TypeDecorator, VARCHAR
from .database import Base

# Custom JSON type for SQLite
class JSONType(TypeDecorator):
    """JSON type for SQLite."""
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)  # Rich text content
    images = Column(JSONType, default=lambda: [])  # List of image URLs/paths
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    is_answered = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # New: Visibility control
    answer_content = Column(Text, nullable=True)
    answer_images = Column(JSONType, default=lambda: []) # New: List of answer image URLs/paths
    answered_at = Column(DateTime, nullable=True)

class AdminUser(Base):
    __tablename__ = "admin_users"
    # Simple admin table
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
