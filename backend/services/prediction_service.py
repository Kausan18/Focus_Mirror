"""
Prediction Service
──────────────────
Orchestration layer between the DL endpoint and the state estimator.

Receives a validated DLPrediction, applies the state estimator,
writes updated state to Redis, checks for events, and stores
significant events in MongoDB.

This is the write path for all real-time attention data.
"""

from datetime import datetime, timezone
from bson import ObjectId

from database.mongodb import get_db
from schemas.prediction import DLPrediction, PredictionResponse, FocusEvent
from schemas.session import LiveSessionState, SessionStatus
from services.state_estimator import state_estimator, check_for_events
from services.session_service import _get_live_state, _write_live_state, _redis_key
from fastapi import HTTPException, status


async def process_prediction(prediction: DLPrediction) -> PredictionResponse:
    """
    Main entry point called by the DL prediction endpoint.

    1. Verify the session is active
    2. Read current live state from Redis
    3. Run state estimator → updated state
    4. Check event engine
    5. Write updated state to Redis
    6. If event fired → store in MongoDB
    7. Return response
    """
    db = get_db()
    session_id = prediction.sessionId

    # ── Step 1: Verify session is active ──────────────────────────────────
    try:
        oid = ObjectId(session_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID"
        )

    session_doc = await db["sessions"].find_one({"_id": oid})
    if not session_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session_doc["status"] != SessionStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is not active")

    # ── Step 2: Read current state from Redis ─────────────────────────────
    current_state = await _get_live_state(session_id)
    if current_state is None:
        # State expired from Redis — reinitialise from zero
        current_state = LiveSessionState()

    previous_state = current_state.model_copy()   # snapshot before update

    # ── Step 3: Run state estimator ───────────────────────────────────────
    updated_state = state_estimator.process(
        prediction=prediction,
        current_state=current_state,
        elapsed_seconds=5.0,   # approximation — real system would track time delta
    )

    # ── Step 4: Check event engine ────────────────────────────────────────
    event_dict = check_for_events(session_id, updated_state, previous_state)

    # ── Step 5: Write updated state to Redis ──────────────────────────────
    await _write_live_state(session_id, updated_state)

    # ── Step 6: Store event in MongoDB if one fired ───────────────────────
    fired_event = None
    if event_dict:
        result = await db["events"].insert_one({
            **event_dict,
            "sessionId": session_id,
            "userId": session_doc["userId"],
            "timestamp": datetime.now(timezone.utc),
            "agentProcessed": False,   # Step 6 (agent) will flip this to True
        })
        fired_event = FocusEvent(
            type=event_dict["type"],
            sessionId=session_id,
            timestamp=datetime.now(timezone.utc),
            severity=event_dict["severity"],
            data=event_dict["data"],
        )

    return PredictionResponse(
        sessionId=session_id,
        stateUpdated=True,
        currentState=updated_state.model_dump(),
        eventFired=fired_event,
    )