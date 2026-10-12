from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId
from fastapi import HTTPException, status

from config import get_settings
from database.mongodb import get_db
from schemas.user import UserCreate, UserInDB, UserResponse

settings = get_settings()

# bcrypt context — this is what hashes and verifies passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Password helpers ─────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── JWT helpers ──────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    """Create a signed JWT with user_id as the subject."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """Decode a JWT and return the user_id. Raises HTTPException on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no subject",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── MongoDB user helpers ─────────────────────────────────────────────────

def _doc_to_user(doc: dict) -> UserInDB:
    """Convert a raw MongoDB document to a UserInDB model."""
    return UserInDB(
        id=str(doc["_id"]),
        name=doc["name"],
        email=doc["email"],
        hashed_password=doc["hashed_password"],
        created_at=doc["created_at"],
        is_active=doc.get("is_active", True),
    )


def _user_to_response(user: UserInDB) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        is_active=user.is_active,
    )


# ─── Core auth operations ─────────────────────────────────────────────────

async def register_user(data: UserCreate) -> UserResponse:
    db = get_db()
    users = db["users"]

    # Check email uniqueness
    existing = await users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Build document — plain password never stored
    doc = {
        "name": data.name,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "created_at": datetime.now(timezone.utc),
        "is_active": True,
    }

    result = await users.insert_one(doc)
    doc["_id"] = result.inserted_id

    return _user_to_response(_doc_to_user(doc))


async def login_user(email: str, password: str) -> tuple[UserInDB, str]:
    """
    Returns (user, access_token) on success.
    Raises 401 on wrong email or wrong password.
    Same error message for both — don't reveal which one was wrong.
    """
    db = get_db()
    users = db["users"]

    doc = await users.find_one({"email": email})

    # Deliberate: same error for "user not found" and "wrong password"
    if not doc or not verify_password(password, doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = _doc_to_user(doc)
    token = create_access_token(user.id)
    return user, token


async def get_user_by_id(user_id: str) -> UserInDB:
    """Fetch a user by their MongoDB ObjectId string. Raises 404 if not found."""
    db = get_db()
    users = db["users"]

    try:
        doc = await users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return _doc_to_user(doc)