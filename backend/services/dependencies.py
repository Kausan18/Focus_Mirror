from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import decode_access_token, get_user_by_id
from schemas.user import UserInDB

# Extracts Bearer token from the Authorization header automatically
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserInDB:
    """
    FastAPI dependency. Add to any route that requires authentication:

        @router.get("/protected")
        async def protected_route(user: UserInDB = Depends(get_current_user)):
            ...

    Decodes the JWT, fetches the user from MongoDB, returns the UserInDB.
    Raises 401 automatically if token is missing, invalid, or expired.
    """
    token = credentials.credentials
    user_id = decode_access_token(token)
    user = await get_user_by_id(user_id)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user