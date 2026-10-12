"""
DL Prediction Router
────────────────────
POST /api/dl/prediction  — receives real or mock predictions from the DL pipeline
GET  /api/dl/mock        — returns a single mock prediction (for testing)
GET  /api/dl/mock/stream — returns N mock predictions simulating a full session
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone

from schemas.prediction import DLPrediction, PredictionResponse
from schemas.user import UserInDB
from services.dependencies import get_current_user
from services.mock_dl import generate_mock_prediction, generate_mock_session
from services import prediction_service

router = APIRouter()


@router.post("/prediction", response_model=PredictionResponse)
async def receive_prediction(
    prediction: DLPrediction,
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Receive a structured DL prediction and run it through the state estimator.
    Called by Member 2's inference pipeline (or mock during dev).
    Requires authentication.
    """
    return await prediction_service.process_prediction(prediction)


@router.get("/mock")
async def get_mock_prediction(
    session_id: str = Query(..., description="Active session ID"),
    elapsed_seconds: float = Query(default=0.0, description="Seconds since session start"),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Generate a single mock DL prediction.
    Useful for Member 3 (frontend) to test the dashboard with realistic data.
    """
    prediction = generate_mock_prediction(
        session_id=session_id,
        elapsed_seconds=elapsed_seconds,
    )
    return prediction


@router.get("/mock/stream")
async def get_mock_session_stream(
    session_id: str = Query(..., description="Session ID"),
    duration_minutes: float = Query(default=60.0, ge=1.0, le=180.0),
    interval_seconds: float = Query(default=5.0, ge=1.0, le=60.0),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Generate a full sequence of mock predictions simulating an entire session.
    Used by Member 4 (analytics) for testing without live camera data.
    Returns list of predictions — does NOT run them through the state estimator.
    """
    predictions = generate_mock_session(
        session_id=session_id,
        duration_minutes=duration_minutes,
        interval_seconds=interval_seconds,
    )
    return {
        "sessionId": session_id,
        "durationMinutes": duration_minutes,
        "predictionCount": len(predictions),
        "predictions": [p.model_dump() for p in predictions],
    }