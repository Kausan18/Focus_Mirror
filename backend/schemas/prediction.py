from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── DL → Backend contract ────────────────────────────────────────────────
# This is the exact shape Member 2's inference module must produce.
# All scores are floats in [0.0, 1.0].

class DLPrediction(BaseModel):
    sessionId: str
    timestamp: datetime
    attention: float    = Field(..., ge=0.0, le=1.0)
    fatigue: float      = Field(..., ge=0.0, le=1.0)
    distraction: float  = Field(..., ge=0.0, le=1.0)
    cognitiveLoad: float = Field(..., ge=0.0, le=1.0)
    confidence: float   = Field(..., ge=0.0, le=1.0)


# ─── Event schemas ────────────────────────────────────────────────────────

class FocusEvent(BaseModel):
    type: str           # SUSTAINED_ATTENTION_DROP | HIGH_FATIGUE | RECOVERY_DETECTED | etc.
    sessionId: str
    timestamp: datetime
    severity: str       # LOW | MEDIUM | HIGH
    data: dict          # event-specific payload


# ─── Prediction endpoint response ─────────────────────────────────────────

class PredictionResponse(BaseModel):
    sessionId: str
    stateUpdated: bool
    currentState: dict          # the updated LiveSessionState as dict
    eventFired: Optional[FocusEvent] = None   # present if an event was triggered