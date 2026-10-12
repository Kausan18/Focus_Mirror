"""
State Estimator
───────────────
Converts instantaneous DL predictions into stable temporal state.

Called on every incoming prediction. Reads current state from Redis,
applies smoothing + trend detection, writes updated state back.

Core principle from system design doc:
  "A single prediction does not establish a meaningful attention state."
"""

from datetime import datetime, timezone
from schemas.prediction import DLPrediction
from schemas.session import LiveSessionState

# ─── Tunable constants ────────────────────────────────────────────────────

# Exponential moving average alpha — controls smoothing speed.
# Lower = smoother but slower to react. Higher = faster but noisier.
# 0.3 means each new value contributes 30% and history contributes 70%.
EMA_ALPHA = 0.3

# Trend detection: if recent EMA differs from longer-term EMA by more
# than this threshold, we declare a trend.
TREND_THRESHOLD = 0.08

# Attention thresholds for event detection
LOW_ATTENTION_THRESHOLD = 0.45      # below this = "low attention"
HIGH_FATIGUE_THRESHOLD  = 0.70      # above this = "high fatigue"
RECOVERY_THRESHOLD      = 0.60      # above this after a drop = "recovery"

# How many seconds of sustained low attention before firing an event
SUSTAINED_DROP_SECONDS  = 120       # 2 minutes

# Hysteresis: once in a DECLINING trend, attention must recover by this
# much above the low threshold before reverting to STABLE
HYSTERESIS_BAND = 0.10


class StateEstimator:
    """
    Stateless class — all state lives in the LiveSessionState dict from Redis.
    Each call takes the current state, applies the new prediction, returns
    the updated state. No instance variables needed.
    """

    def process(
        self,
        prediction: DLPrediction,
        current_state: LiveSessionState,
        elapsed_seconds: float = 5.0,   # time since last prediction (approx)
    ) -> LiveSessionState:
        """
        Apply a new DL prediction to the current live state.
        Returns an updated LiveSessionState — does NOT write to Redis itself.
        The caller (prediction service) handles the Redis write.
        """

        # ── Step 1: Exponential Moving Average ───────────────────────────
        # First prediction initialises the EMA. Subsequent predictions smooth.
        if current_state.attention == 0.0 and current_state.fatigue == 0.0:
            # First prediction — initialise directly, don't smooth
            smoothed_attention    = prediction.attention
            smoothed_fatigue      = prediction.fatigue
            smoothed_distraction  = prediction.distraction
            smoothed_cognitive    = prediction.cognitiveLoad
        else:
            smoothed_attention   = _ema(prediction.attention,    current_state.attention,    EMA_ALPHA)
            smoothed_fatigue     = _ema(prediction.fatigue,      current_state.fatigue,      EMA_ALPHA)
            smoothed_distraction = _ema(prediction.distraction,  current_state.distraction,  EMA_ALPHA)
            smoothed_cognitive   = _ema(prediction.cognitiveLoad, current_state.cognitiveLoad, EMA_ALPHA)

        # ── Step 2: Trend detection ───────────────────────────────────────
        # Compare smoothed attention (recent) against what we had before (historical proxy).
        # A more sophisticated version would maintain a second slower EMA for
        # the "long-term" baseline — for MVP, the previous state serves as proxy.
        previous_attention = current_state.attention
        trend = _detect_trend(
            current_smoothed=smoothed_attention,
            previous=previous_attention,
            current_trend=current_state.attentionTrend,
        )

        # ── Step 3: Duration tracking ─────────────────────────────────────
        # Track consecutive seconds of low attention.
        if smoothed_attention < LOW_ATTENTION_THRESHOLD:
            low_attention_duration = current_state.lowAttentionDuration + int(elapsed_seconds)
        else:
            # Reset if attention has recovered above the hysteresis band
            if smoothed_attention >= (LOW_ATTENTION_THRESHOLD + HYSTERESIS_BAND):
                low_attention_duration = 0
            else:
                # Still low but crossing threshold — don't reset yet
                low_attention_duration = current_state.lowAttentionDuration

        return LiveSessionState(
            attention=round(smoothed_attention, 4),
            fatigue=round(smoothed_fatigue, 4),
            distraction=round(smoothed_distraction, 4),
            cognitiveLoad=round(smoothed_cognitive, 4),
            attentionTrend=trend,
            lowAttentionDuration=low_attention_duration,
            lastIntervention=current_state.lastIntervention,
            interventionsIgnored=current_state.interventionsIgnored,
            lastUpdated=datetime.now(timezone.utc).isoformat(),
        )


# ─── Event Engine ─────────────────────────────────────────────────────────

def check_for_events(
    session_id: str,
    updated_state: LiveSessionState,
    previous_state: LiveSessionState,
) -> dict | None:
    """
    Examine the updated state for meaningful events.
    Returns an event dict if one is detected, None otherwise.

    The agent (Step 6) only fires when this returns something.
    This is the gate that prevents calling the LLM on every frame.
    """

    now = datetime.now(timezone.utc).isoformat()

    # ── SUSTAINED_ATTENTION_DROP ──────────────────────────────────────────
    # Attention has been below threshold for long enough to act on.
    # Only fire once per drop (not on every subsequent prediction).
    if (
        updated_state.lowAttentionDuration >= SUSTAINED_DROP_SECONDS
        and updated_state.lowAttentionDuration - int(5) < SUSTAINED_DROP_SECONDS
        # The subtraction checks: we just crossed the threshold this prediction,
        # not that we've been above it for many predictions already.
        # A cleaner implementation would use a flag in state — sufficient for MVP.
    ):
        severity = _attention_severity(updated_state.attention)
        return {
            "type": "SUSTAINED_ATTENTION_DROP",
            "sessionId": session_id,
            "timestamp": now,
            "severity": severity,
            "data": {
                "attention": updated_state.attention,
                "duration": updated_state.lowAttentionDuration,
                "fatigue": updated_state.fatigue,
                "trend": updated_state.attentionTrend,
            }
        }

    # ── HIGH_FATIGUE ──────────────────────────────────────────────────────
    if (
        updated_state.fatigue >= HIGH_FATIGUE_THRESHOLD
        and previous_state.fatigue < HIGH_FATIGUE_THRESHOLD
    ):
        return {
            "type": "HIGH_FATIGUE",
            "sessionId": session_id,
            "timestamp": now,
            "severity": "HIGH" if updated_state.fatigue >= 0.85 else "MEDIUM",
            "data": {
                "fatigue": updated_state.fatigue,
                "attention": updated_state.attention,
            }
        }

    # ── RECOVERY_DETECTED ─────────────────────────────────────────────────
    # Attention was low, now it's recovering — good signal to reinforce.
    if (
        previous_state.attention < LOW_ATTENTION_THRESHOLD
        and updated_state.attention >= RECOVERY_THRESHOLD
        and previous_state.lowAttentionDuration > 30   # was low for at least 30s
    ):
        return {
            "type": "RECOVERY_DETECTED",
            "sessionId": session_id,
            "timestamp": now,
            "severity": "LOW",
            "data": {
                "attention": updated_state.attention,
                "previousAttention": previous_state.attention,
                "recoveryFromDuration": previous_state.lowAttentionDuration,
            }
        }

    return None


# ─── Internal helpers ─────────────────────────────────────────────────────

def _ema(new_value: float, old_value: float, alpha: float) -> float:
    """Exponential moving average: new * alpha + old * (1 - alpha)"""
    return new_value * alpha + old_value * (1 - alpha)


def _detect_trend(
    current_smoothed: float,
    previous: float,
    current_trend: str,
) -> str:
    delta = current_smoothed - previous

    if delta < -TREND_THRESHOLD:
        return "DECLINING"
    elif delta > TREND_THRESHOLD:
        return "IMPROVING"
    else:
        # Hysteresis: if already declining, require stronger recovery to flip
        if current_trend == "DECLINING" and current_smoothed < (LOW_ATTENTION_THRESHOLD + HYSTERESIS_BAND):
            return "DECLINING"
        return "STABLE"


def _attention_severity(attention: float) -> str:
    if attention < 0.25:
        return "HIGH"
    elif attention < 0.35:
        return "MEDIUM"
    return "LOW"


# ─── Singleton ────────────────────────────────────────────────────────────
# Stateless — safe to share across requests
state_estimator = StateEstimator()