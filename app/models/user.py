from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from .base import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    __tablename__ = "users"
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    assigned_stories = relationship("UserStory", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")
    
    def verify_password(self, plain_password: str) -> bool:
        """Verify a password against the hash"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def set_password(self, password: str):
        """Set password for user"""
        self.hashed_password = self.get_password_hash(password)
