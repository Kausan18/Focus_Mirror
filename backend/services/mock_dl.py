"""
Mock DL Prediction Generator
─────────────────────────────
Simulates realistic attention/fatigue/distraction curves for a focus session.
Used by Member 3 (frontend) and Member 1 (agent) while Member 2's real
PyTorch model is being developed.

Produces the exact same JSON shape as the real DL contract, so swapping
in the real model requires zero changes to the backend.
"""

import random
import math
from datetime import datetime, timezone
from schemas.prediction import DLPrediction


def generate_mock_prediction(
    session_id: str,
    elapsed_seconds: float = 0.0,
    seed: float | None = None,
) -> DLPrediction:
    """
    Generate a single realistic mock prediction.

    Simulates a realistic focus session pattern:
    - Attention starts moderately high (~0.75), gradually declines over time
    - Fatigue starts low, gradually increases
    - Distraction inversely tracks attention with some lag
    - Natural gaussian noise on all signals
    - Attention dip around the 30-50 minute mark (common in real sessions)

    elapsed_seconds: seconds since session start — drives the time-based curve
    """

    if seed is not None:
        random.seed(seed)

    minutes = elapsed_seconds / 60.0

    # ── Attention curve ────────────────────────────────────────────────────
    # Starts ~0.75, slowly declines. Sharper dip around 35-50 min.
    base_attention = 0.75 - (minutes * 0.004)                         # slow linear decline
    dip = 0.15 * math.exp(-((minutes - 40) ** 2) / (2 * 15 ** 2))    # gaussian dip at ~40min
    attention = base_attention - dip + random.gauss(0, 0.05)
    attention = _clamp(attention, 0.10, 0.95)

    # ── Fatigue curve ──────────────────────────────────────────────────────
    # Starts ~0.15, increases with time + correlates with low attention
    base_fatigue = 0.15 + (minutes * 0.005)
    fatigue_spike = 0.10 * math.exp(-((minutes - 45) ** 2) / (2 * 20 ** 2))
    fatigue = base_fatigue + fatigue_spike + random.gauss(0, 0.04)
    # Fatigue inversely correlates with attention
    fatigue += (0.75 - attention) * 0.3
    fatigue = _clamp(fatigue, 0.05, 0.95)

    # ── Distraction ────────────────────────────────────────────────────────
    # Inversely tracks attention with some lag and noise
    distraction = (1.0 - attention) * 0.6 + random.gauss(0, 0.06)
    distraction = _clamp(distraction, 0.05, 0.90)

    # ── Cognitive load ─────────────────────────────────────────────────────
    # Relatively stable — task-dependent. Moderate baseline with noise.
    cognitive_load = 0.50 + random.gauss(0, 0.08)
    cognitive_load = _clamp(cognitive_load, 0.20, 0.85)

    # ── Confidence ────────────────────────────────────────────────────────
    # Simulates model confidence — high when face clearly visible
    confidence = 0.88 + random.gauss(0, 0.05)
    confidence = _clamp(confidence, 0.60, 0.99)

    return DLPrediction(
        sessionId=session_id,
        timestamp=datetime.now(timezone.utc),
        attention=round(attention, 4),
        fatigue=round(fatigue, 4),
        distraction=round(distraction, 4),
        cognitiveLoad=round(cognitive_load, 4),
        confidence=round(confidence, 4),
    )


def generate_mock_session(
    session_id: str,
    duration_minutes: float = 60.0,
    interval_seconds: float = 5.0,
) -> list[DLPrediction]:
    """
    Generate a full sequence of predictions simulating an entire session.
    Used by Member 4 (analytics) for testing without live data.
    """
    predictions = []
    elapsed = 0.0
    while elapsed <= duration_minutes * 60:
        pred = generate_mock_prediction(session_id, elapsed_seconds=elapsed)
        predictions.append(pred)
        elapsed += interval_seconds
    return predictions


def _clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))