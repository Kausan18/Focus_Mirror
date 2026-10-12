from fastapi import APIRouter, Depends, Query, status

from schemas.session import SessionStart, SessionResponse
from schemas.user import UserInDB
from services.dependencies import get_current_user
from services import session_service

router = APIRouter()


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    data: SessionStart,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Start a new focus session.
    409 if the user already has an active session.
    """
    return await session_service.start_session(current_user.id, data)


@router.post("/end/{session_id}", response_model=SessionResponse)
async def end_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    End an active session. Writes the final summary to MongoDB.
    403 if the session belongs to a different user.
    409 if the session is already ended.
    """
    return await session_service.end_session(current_user.id, session_id)


@router.get("/current", response_model=SessionResponse)
async def get_current_session(
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get the user's currently active session, including live state from Redis.
    404 if no active session.
    """
    return await session_service.get_current_session(current_user.id)


@router.get("/history", response_model=list[SessionResponse])
async def get_session_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get the user's session history, newest first.
    """
    return await session_service.get_session_history(current_user.id, limit)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Get a specific session by ID.
    403 if it belongs to a different user.
    """
    return await session_service.get_session_by_id(current_user.id, session_id)