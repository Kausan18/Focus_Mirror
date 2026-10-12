import json
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException, status

from database.mongodb import get_db
from database.redis import get_redis
from schemas.session import (
    SessionStart, SessionInDB, SessionResponse,
    SessionStatus, LiveSessionState
)

# Redis TTL: auto-expire live state 2 hours after last write.
# Protects against sessions that were never explicitly ended (e.g. browser closed).
SESSION_STATE_TTL_SECONDS = 7200  # 2 hours

# Redis key pattern — consistent across all services
def _redis_key(session_id: str) -> str:
    return f"session:{session_id}:state"


# ─── Internal helpers ─────────────────────────────────────────────────────

def _doc_to_session(doc: dict) -> SessionInDB:
    return SessionInDB(
        id=str(doc["_id"]),
        userId=str(doc["userId"]),
        mode=doc["mode"],
        status=doc["status"],
        taskType=doc.get("taskType"),
        startTime=doc["startTime"],
        endTime=doc.get("endTime"),
        durationSeconds=doc.get("durationSeconds"),
        averageAttention=doc.get("averageAttention"),
        averageFatigue=doc.get("averageFatigue"),
        averageDistraction=doc.get("averageDistraction"),
        averageCognitiveLoad=doc.get("averageCognitiveLoad"),
        totalInterventions=doc.get("totalInterventions", 0),
        acceptedInterventions=doc.get("acceptedInterventions", 0),
    )


def _build_response(session: SessionInDB, live: Optional[LiveSessionState] = None) -> SessionResponse:
    resp = SessionResponse(
        id=session.id,
        userId=session.userId,
        mode=session.mode,
        status=session.status,
        taskType=session.taskType,
        startTime=session.startTime,
        endTime=session.endTime,
        durationSeconds=session.durationSeconds,
        averageAttention=session.averageAttention,
        averageFatigue=session.averageFatigue,
        totalInterventions=session.totalInterventions,
        acceptedInterventions=session.acceptedInterventions,
    )
    # Merge live state if available (active session)
    if live:
        resp.attention = live.attention
        resp.fatigue = live.fatigue
        resp.distraction = live.distraction
        resp.cognitiveLoad = live.cognitiveLoad
        resp.attentionTrend = live.attentionTrend
    return resp


async def _get_live_state(session_id: str) -> Optional[LiveSessionState]:
    """Read current state from Redis. Returns None if key doesn't exist."""
    redis = get_redis()
    raw = await redis.get(_redis_key(session_id))
    if not raw:
        return None
    data = json.loads(raw)
    return LiveSessionState(**data)


async def _write_live_state(session_id: str, state: LiveSessionState):
    """Write (or refresh) live state in Redis with TTL."""
    redis = get_redis()
    await redis.set(
        _redis_key(session_id),
        state.model_dump_json(),
        ex=SESSION_STATE_TTL_SECONDS,
    )


async def _delete_live_state(session_id: str):
    redis = get_redis()
    await redis.delete(_redis_key(session_id))


# ─── Core session operations ──────────────────────────────────────────────

async def start_session(user_id: str, data: SessionStart) -> SessionResponse:
    db = get_db()
    sessions = db["sessions"]

    # Enforce one active session per user
    existing = await sessions.find_one({"userId": ObjectId(user_id), "status": SessionStatus.ACTIVE})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Session already active: {str(existing['_id'])}. End it before starting a new one.",
        )

    now = datetime.now(timezone.utc)
    doc = {
        "userId": ObjectId(user_id),
        "mode": data.mode,
        "status": SessionStatus.ACTIVE,
        "taskType": data.taskType,
        "startTime": now,
        "endTime": None,
        "durationSeconds": None,
        "totalInterventions": 0,
        "acceptedInterventions": 0,
    }

    result = await sessions.insert_one(doc)
    session_id = str(result.inserted_id)

    # Initialize live state in Redis — zeroed out, DL pipeline will populate it
    initial_state = LiveSessionState(
        lastUpdated=now.isoformat()
    )
    await _write_live_state(session_id, initial_state)

    doc["_id"] = result.inserted_id
    session = _doc_to_session(doc)
    return _build_response(session, initial_state)


async def end_session(user_id: str, session_id: str) -> SessionResponse:
    db = get_db()
    sessions = db["sessions"]

    try:
        oid = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session ID")

    doc = await sessions.find_one({"_id": oid})

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if str(doc["userId"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")

    if doc["status"] == SessionStatus.ENDED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session already ended")

    # Read final live state before deleting from Redis
    live = await _get_live_state(session_id)

    now = datetime.now(timezone.utc)
    duration = int((now - doc["startTime"].replace(tzinfo=timezone.utc)).total_seconds())

    update = {
        "status": SessionStatus.ENDED,
        "endTime": now,
        "durationSeconds": duration,
    }

    # If we have live state, write it as the session summary
    # In a real system, the state estimator accumulates running averages —
    # for now we store the final snapshot values as the summary.
    if live:
        update["averageAttention"] = live.attention
        update["averageFatigue"] = live.fatigue
        update["averageDistraction"] = live.distraction
        update["averageCognitiveLoad"] = live.cognitiveLoad

    await sessions.update_one({"_id": oid}, {"$set": update})
    await _delete_live_state(session_id)

    # Fetch the updated doc to return
    updated_doc = await sessions.find_one({"_id": oid})
    session = _doc_to_session(updated_doc)
    return _build_response(session)


async def get_current_session(user_id: str) -> SessionResponse:
    db = get_db()
    sessions = db["sessions"]

    doc = await sessions.find_one(
        {"userId": ObjectId(user_id), "status": SessionStatus.ACTIVE}
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session"
        )

    session = _doc_to_session(doc)
    live = await _get_live_state(session.id)
    return _build_response(session, live)


async def get_session_by_id(user_id: str, session_id: str) -> SessionResponse:
    db = get_db()
    sessions = db["sessions"]

    try:
        oid = ObjectId(session_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session ID")

    doc = await sessions.find_one({"_id": oid})

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if str(doc["userId"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")

    session = _doc_to_session(doc)

    # If somehow still active, include live state
    live = None
    if session.status == SessionStatus.ACTIVE:
        live = await _get_live_state(session_id)

    return _build_response(session, live)


async def get_session_history(user_id: str, limit: int = 20) -> list[SessionResponse]:
    db = get_db()
    sessions = db["sessions"]

    cursor = sessions.find(
        {"userId": ObjectId(user_id)},
        sort=[("startTime", -1)],   # newest first
        limit=limit,
    )

    results = []
    async for doc in cursor:
        session = _doc_to_session(doc)
        results.append(_build_response(session))

    return results


# ─── Internal: used by Step 4 state estimator to write DL predictions ─────

async def update_live_state(session_id: str, updates: dict):
    """
    Called by the state estimator after processing DL predictions.
    Reads current state, merges updates, writes back to Redis.
    This is the write path for real-time attention data.
    """
    redis = get_redis()
    raw = await redis.get(_redis_key(session_id))

    if raw:
        current = json.loads(raw)
        current.update(updates)
        current["lastUpdated"] = datetime.now(timezone.utc).isoformat()
        state = LiveSessionState(**current)
    else:
        # Session state expired or doesn't exist — initialize fresh
        updates["lastUpdated"] = datetime.now(timezone.utc).isoformat()
        state = LiveSessionState(**updates)

    await _write_live_state(session_id, state)
    return state