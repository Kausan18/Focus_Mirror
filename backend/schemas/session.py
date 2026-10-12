from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ─── Session mode — maps to system design doc section 22 ──────────────────
class SessionMode(str, Enum):
    STUDY      = "STUDY"
    WORK       = "WORK"
    DEEP_WORK  = "DEEP_WORK"
    MEETING    = "MEETING"
    VIGILANCE  = "VIGILANCE"
    CUSTOM     = "CUSTOM"


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED  = "ENDED"


# ─── Input: what the client sends to start a session ─────────────────────
class SessionStart(BaseModel):
    mode: SessionMode = SessionMode.WORK
    taskType: Optional[str] = None   # e.g. "CODING", "DEBUGGING" — optional at start


# ─── What we store in MongoDB ─────────────────────────────────────────────
class SessionInDB(BaseModel):
    id: str
    userId: str
    mode: SessionMode
    status: SessionStatus
    taskType: Optional[str]
    startTime: datetime
    endTime: Optional[datetime] = None
    durationSeconds: Optional[int] = None
    # Summary written on session end
    averageAttention: Optional[float] = None
    averageFatigue: Optional[float] = None
    averageDistraction: Optional[float] = None
    averageCognitiveLoad: Optional[float] = None
    totalInterventions: int = 0
    acceptedInterventions: int = 0


# ─── Live state stored in Redis ───────────────────────────────────────────
class LiveSessionState(BaseModel):
    attention: float = 0.0
    fatigue: float = 0.0
    distraction: float = 0.0
    cognitiveLoad: float = 0.0
    attentionTrend: str = "STABLE"       # IMPROVING | STABLE | DECLINING
    lowAttentionDuration: int = 0        # seconds of sustained low attention
    lastIntervention: Optional[str] = None
    interventionsIgnored: int = 0
    lastUpdated: Optional[str] = None    # ISO timestamp


# ─── API response: session + live state merged ────────────────────────────
class SessionResponse(BaseModel):
    id: str
    userId: str
    mode: SessionMode
    status: SessionStatus
    taskType: Optional[str]
    startTime: datetime
    endTime: Optional[datetime] = None
    durationSeconds: Optional[int] = None
    # Live state fields — present when session is ACTIVE
    attention: Optional[float] = None
    fatigue: Optional[float] = None
    distraction: Optional[float] = None
    cognitiveLoad: Optional[float] = None
    attentionTrend: Optional[str] = None
    # Summary fields — present when session is ENDED
    averageAttention: Optional[float] = None
    averageFatigue: Optional[float] = None
    totalInterventions: int = 0
    acceptedInterventions: int = 0