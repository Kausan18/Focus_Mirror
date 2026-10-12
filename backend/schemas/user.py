from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ─── Input: what the client sends on register ─────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


# ─── Input: what the client sends on login ────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ─── Internal: what we store in / read from MongoDB ───────────────────────
class UserInDB(BaseModel):
    id: str                        # MongoDB _id as string
    name: str
    email: str
    hashed_password: str
    created_at: datetime
    is_active: bool = True


# ─── Output: what we return to the client (never includes password) ────────
class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    is_active: bool


# ─── Output: login response wraps token + user ────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse