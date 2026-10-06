# FocusMirror — Complete System Design

## 1. Project Overview

**FocusMirror** is a real-time cognitive load and attention monitoring system combining Computer Vision, Deep Learning, temporal state estimation, event detection, AI agents, personalization, real-time communication, and privacy-aware analytics.

Core principle:

> **Perception → State → Event → Reasoning → Action → Feedback → Personalization**

---

## 2. High-Level Architecture

```text
                         USER
                           │
                           ▼
                  React / Next.js
                       Frontend
                           │
             ┌─────────────┴─────────────┐
             │                           │
           WebRTC                  REST / WebSocket
             │                           │
             ▼                           ▼
      OpenCV → MediaPipe → PyTorch     NGINX
             │                           │
             │                           ▼
             │                       FastAPI
             │                           │
             ▼                           ▼
       DL Predictions                  Redis
             │                       Hot State
             ▼                           │
       State Estimator ◄───────────────┘
             │
             ▼
       Event Detection
             │
             ▼
       Context Builder
       Redis + MongoDB
       Preferences + Analytics
             │
             ▼
      LangGraph + LangChain
             │
             ▼
             LLM
             │
             ▼
       Tool Selection
             │
             ▼
       Policy / Guardrails
             │
             ▼
        Tool Execution
             │
             ▼
         WebSocket
             │
             ▼
          Frontend
             │
             ▼
       User Response
          /                 ▼          ▼
      Redis      MongoDB
                  │
                  ▼
       Analytics / Personalization
                  │
                  └──────► Agent Context
```

---

## 3. Communication Architecture

FocusMirror uses three communication mechanisms for different jobs.

### REST / HTTP

Used for normal request-response operations:

```text
POST /api/auth/login
POST /api/session/start
POST /api/session/end
GET  /api/session/current
GET  /api/session/history
GET  /api/focus/current
GET  /api/focus/fingerprint
PUT  /api/preferences
GET  /api/privacy/settings
DELETE /api/privacy/history
```

### WebSocket

Used for realtime application events:

```text
/ws/session/{sessionId}
```

Backend → Frontend:

```text
STATE_UPDATE
FOCUS_ALERT
INTERVENTION
AGENT_MESSAGE
SESSION_END
```

Frontend → Backend:

```text
INTERVENTION_RESPONSE
USER_ACTION
SESSION_CONTROL
ACKNOWLEDGEMENT
```

### WebRTC

Used for actual camera/media transport:

```text
Camera → WebRTC → Inference Pipeline
```

**Rule:** WebRTC carries media, WebSocket carries realtime application events, and REST handles normal application requests.

---

# 4. Perception Plane

The perception plane answers:

> **What is happening right now?**

Pipeline:

```text
Camera
  ↓
WebRTC
  ↓
OpenCV
  ↓
MediaPipe
  ↓
Feature Extraction
  ↓
PyTorch
  ↓
Attention / Fatigue / Distraction / Cognitive Load
```

### OpenCV

Responsibilities:

- Frame preprocessing
- Resize/crop
- Normalization
- Frame sampling
- Image quality checks
- Face-region processing

### MediaPipe

Can provide:

- Face landmarks
- Eye landmarks
- Head orientation
- Blink-related features
- Facial geometry
- Pose information

Possible features:

```text
Eye Aspect Ratio
Blink Rate
Eye Closure Duration
Head Pose
Gaze Direction
Facial Movement
Posture
```

### PyTorch

Produces learned estimates such as:

```json
{
  "attention": 0.72,
  "fatigue": 0.31,
  "distraction": 0.18,
  "cognitiveLoad": 0.54,
  "confidence": 0.91
}
```

These are behavioral estimates, not medical diagnoses.

---

# 5. Training vs Runtime

## Offline Training

```text
Dataset
 ↓
Preprocessing
 ↓
Feature Engineering
 ↓
Training
 ↓
Validation
 ↓
Evaluation
 ↓
Model Artifact
```

Google Colab can be used for training and experiments.

## Runtime

```text
Camera
 ↓
Preprocessing
 ↓
Landmarks / Features
 ↓
Trained Model
 ↓
Prediction
```

Colab is therefore primarily a training environment, not a required live-runtime component.

---

# 6. DL → Backend Contract

The DL pipeline should not send raw webcam frames to the agent.

It produces structured predictions:

```json
{
  "sessionId": "S456",
  "timestamp": "2026-09-18T10:30:00Z",
  "attention": 0.72,
  "fatigue": 0.31,
  "distraction": 0.18,
  "cognitiveLoad": 0.54,
  "confidence": 0.91
}
```

A mock mode such as:

```text
mock_dl_prediction()
```

should exist so backend and frontend work can proceed before the final model is ready.

---

# 7. State Plane

A single prediction does not establish a meaningful attention state.

The system therefore converts instantaneous predictions into a temporal state using:

- Sliding windows
- Moving averages
- Smoothing
- Thresholds
- Trend detection
- Hysteresis
- Duration tracking

Example:

```json
{
  "attention": 0.38,
  "fatigue": 0.76,
  "distraction": 0.71,
  "cognitiveLoad": 0.54,
  "sessionDuration": 5400,
  "attentionTrend": "DECLINING",
  "continuousLowAttentionDuration": 180,
  "lastIntervention": "NOTIFICATION",
  "interventionsIgnored": 2
}
```

---

# 8. Redis — Hot/Current State

Mental model:

> **Redis = what is happening right now.**

Example key:

```text
session:S456:state
```

Possible contents:

```json
{
  "attention": 0.38,
  "fatigue": 0.76,
  "distraction": 0.71,
  "trend": "DECLINING",
  "lowAttentionDuration": 180,
  "lastIntervention": "NOTIFICATION"
}
```

Redis can also support:

- TTL
- Rate limiting
- Cooldowns
- Locks
- Temporary agent state
- Streams where useful

---

# 9. MongoDB — Persistent History

Mental model:

> **MongoDB = what happened before and what should be remembered.**

Possible collections:

```text
users
sessions
events
interventions
reports
agent_logs
focus_profiles
preferences
analytics
```

Store:

- User profile
- Preferences
- Session metadata
- Meaningful events
- Intervention history
- Agent decisions/logs
- Focus Fingerprint
- Analytics
- Reports

Raw webcam frames should not be stored by default.

---

# 10. Event Engine

The event engine converts continuous state into meaningful events.

Do **not** invoke the LLM for every frame.

Bad:

```text
Camera → DL → LLM → LLM → LLM → ...
```

Correct:

```text
Camera
 ↓
DL
 ↓
Temporal State
 ↓
Event Engine
 ↓
Agent
```

Example:

```json
{
  "type": "SUSTAINED_ATTENTION_DROP",
  "sessionId": "S456",
  "timestamp": "2026-09-18T10:35:00Z",
  "attention": 0.38,
  "duration": 180
}
```

Possible events:

```text
SUSTAINED_ATTENTION_DROP
HIGH_FATIGUE
HIGH_DISTRACTION
COGNITIVE_LOAD_SPIKE
RECOVERY_DETECTED
SESSION_STARTED
SESSION_ENDED
```

---

# 11. Agent Plane

The agent answers:

> **Given the current situation and user history, what should the system do?**

The agent receives structured context rather than raw images.

Example:

```json
{
  "currentState": {
    "attention": 0.32,
    "fatigue": 0.78,
    "distraction": 0.71,
    "lowAttentionDuration": 180,
    "trend": "DECLINING"
  },
  "sessionState": {
    "sessionDuration": 5400,
    "lastIntervention": "30 minutes ago",
    "interventionsIgnored": 2
  },
  "userPreferences": {
    "preferredBreakDuration": 5,
    "preferredIntervention": "SHORT_WALK"
  },
  "history": {
    "shortWalkAcceptanceRate": 0.78,
    "averageRecoveryTime": 8
  }
}
```

---

# 12. LangGraph + LangChain

LangGraph manages the stateful workflow:

```text
EVENT
  ↓
Context Builder
  ↓
Agent State
  ↓
LLM Reasoning
  ↓
Action Selection
  ↓
Policy / Guardrail
  ├── BLOCK
  └── ALLOW
        ↓
       Tool
        ↓
    Tool Result
        ↓
   State Update
        ↓
       END
```

LangChain handles components such as:

- LLM integration
- Prompt templates
- Structured output
- Tool definitions
- Tool calling
- Context formatting
- Retrieval where required

---

# 13. Agent Tools

Possible tools:

```text
send_notification()
suggest_break()
suggest_walk()
start_focus_timer()
generate_focus_summary()
retrieve_user_history()
retrieve_focus_profile()
update_schedule()
```

Example action:

```json
{
  "action": "SUGGEST_BREAK",
  "type": "SHORT_WALK",
  "duration": 5,
  "reason": "Sustained attention decline"
}
```

Tools should have explicit schemas, validation, authorization and error handling.

---

# 14. Agent Guardrails

The LLM should never have unrestricted access to the system.

Correct pattern:

```text
LLM
 ↓
Tool Proposal
 ↓
Policy / Guardrail
 ↓
Validation
 ↓
Tool Execution
```

Example checks:

```text
Are notifications enabled?
Is the cooldown active?
Was an intervention recently sent?
Is the session active?
```

Core principle:

> **AI proposes/reasons; deterministic software validates, authorizes and executes.**

---

# 15. Backend Architecture

FastAPI is the primary backend.

Suggested structure:

```text
backend/
│
├── main.py
│
├── api/
│   ├── auth.py
│   ├── sessions.py
│   ├── focus.py
│   ├── users.py
│   ├── preferences.py
│   ├── privacy.py
│   └── agent.py
│
├── websocket/
│   └── session_ws.py
│
├── services/
│   ├── session_service.py
│   ├── state_service.py
│   ├── event_service.py
│   └── intervention_service.py
│
├── database/
│   ├── mongodb.py
│   └── redis.py
│
├── agent/
│   ├── graph.py
│   ├── state.py
│   ├── prompts.py
│   ├── tools.py
│   ├── policies.py
│   └── context.py
│
└── schemas/
    ├── api.py
    ├── events.py
    ├── predictions.py
    └── agent.py
```

---

# 16. REST API Surface

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

## Sessions

```text
POST /api/session/start
POST /api/session/end
GET  /api/session/current
GET  /api/session/{sessionId}
GET  /api/session/history
```

## Focus

```text
GET /api/focus/current
GET /api/focus/history
GET /api/focus/summary
GET /api/focus/fingerprint
```

## User / Preferences

```text
GET /api/user/profile
PUT /api/user/profile
GET /api/preferences
PUT /api/preferences
```

## Privacy

```text
GET    /api/privacy/settings
PUT    /api/privacy/settings
DELETE /api/privacy/history
DELETE /api/privacy/session/{sessionId}
```

---

# 17. WebSocket Architecture

Endpoint:

```text
/ws/session/{sessionId}
```

Backend → Frontend:

```json
{
  "type": "STATE_UPDATE",
  "payload": {
    "attention": 0.72,
    "fatigue": 0.31,
    "distraction": 0.18
  }
}
```

Intervention:

```json
{
  "type": "INTERVENTION",
  "interventionId": "I789",
  "recommendation": {
    "type": "SHORT_WALK",
    "duration": 5
  }
}
```

Frontend response:

```json
{
  "type": "INTERVENTION_RESPONSE",
  "interventionId": "I789",
  "response": "ACCEPTED"
}
```

---

# 18. NGINX API Gateway

```text
Frontend
   ↓
NGINX
   ├── /api/*
   └── /ws/*
          ↓
       FastAPI
```

NGINX handles:

- Reverse proxy
- Routing
- TLS termination
- Rate limiting
- WebSocket proxying
- Load balancing if needed
- Static frontend serving if required

NGINX does not perform attention inference or agent reasoning.

---

# 19. Analytics & Personalization

Analytics can calculate:

- Focus Fingerprint
- Attention trends
- Intervention acceptance
- Intervention effectiveness
- Recovery time
- Task-specific cognitive load
- Weekly insights
- Adaptive scheduling recommendations

## Focus Fingerprint

Example:

```text
FOCUS FINGERPRINT

Peak Focus:
10:00 AM – 12:00 PM

Average Continuous Focus:
47 minutes

Average Recovery:
8 minutes

Best Task:
Coding

Highest Cognitive Load:
Debugging

Frequent Attention Drop:
2:30 PM – 4:00 PM
```

## Intervention Effectiveness

```text
Attention Before = 0.38
Intervention = SHORT_WALK
Attention After = 0.71
```

Possible metrics:

```text
Recovery Improvement
Acceptance Rate
Average Recovery Time
Intervention Effectiveness
```

## Personalization

Example:

```text
SHORT_WALK
Acceptance = 78%

COFFEE_BREAK
Acceptance = 61%

BREATHING
Acceptance = 43%
```

The system can prioritize interventions that historically work better for that user.

Important:

> Store and use historical behavior for personalization. Do not claim that the system performs online model training unless an actual online learning system has been implemented.

---

# 20. Task-Specific Cognitive Load

The system can associate cognitive load with task type:

| Task | Typical Load |
|---|---|
| Documentation | Low |
| Coding | Medium |
| Debugging | High |
| Meetings | Medium |
| Data Analysis | High |

Initially, task type can be selected manually.

Future sources could include:

- Calendar
- IDE context
- Browser context
- Task-management systems

---

# 21. Adaptive Workday

Inputs:

```text
Calendar
+
Tasks
+
Focus Fingerprint
+
Current Attention
+
User Preferences
+
Historical Performance
```

Example:

```text
Peak focus: 10 AM – 12 PM
High complexity task: Debugging
Scheduled: 3 PM
```

Possible recommendation:

> Move the debugging task to your morning focus window?

The analytics module produces the underlying recommendation; the agent can explain and deliver it; the frontend displays it.

---

# 22. FocusMirror Modes

Possible modes:

```text
Study
Work
Deep Work
Meeting
Vigilance
Custom
```

Modes can modify:

- Event thresholds
- Intervention policy
- Agent behavior
- UI
- Analytics interpretation

The underlying perception pipeline remains largely shared.

---

# 23. Privacy Architecture

Privacy is a core design principle.

Preferred flow:

```text
Camera
 ↓
Local / Controlled Processing
 ↓
Structured Signals
 ↓
Backend
```

Avoid unnecessary storage of raw video.

Example privacy dashboard:

```text
Camera Feed          LOCAL PROCESSING
Raw Video Storage    OFF
Cloud Upload         OFF
Face Identification  OFF
Biometric Database   OFF
```

Stored information can include:

```text
Attention Scores
Cognitive Load Estimates
Session Timestamps
Meaningful Events
Intervention History
Analytics
```

Users should be able to:

- Disable camera processing
- Disable personalization
- Delete history
- Delete sessions
- Control notification behavior

---

# 24. End-to-End Session Workflow

1. User opens FocusMirror.
2. Frontend calls `POST /api/session/start`.
3. FastAPI authenticates the user and creates a session.
4. Redis is initialized with current session state.
5. MongoDB stores durable session metadata.
6. Frontend establishes WebRTC and WebSocket.
7. Camera frames enter the perception pipeline.
8. OpenCV preprocesses frames.
9. MediaPipe extracts landmarks/features.
10. PyTorch generates attention/fatigue/distraction/cognitive-load predictions.
11. State estimator aggregates predictions over time.
12. Redis is updated.
13. Event engine detects a meaningful event.
14. Context builder gathers current state, session data, preferences, history and analytics.
15. LangGraph executes the agent workflow.
16. LLM reasons over the structured context.
17. Agent proposes an action/tool.
18. Deterministic policy validates the proposal.
19. Tool executes the allowed action.
20. Backend sends the intervention over WebSocket.
21. User accepts or dismisses it.
22. Response is stored in Redis/MongoDB.
23. Recovery is measured.
24. Analytics updates the user's behavioral profile.
25. Future agent decisions can use the updated profile.
26. Session end persists the final summary.

---

# 25. Complete Data Transformation

```text
Raw Webcam Frame
        ↓
Processed Image / Tensor
        ↓
Landmarks / Features
        ↓
ML Predictions
        ↓
Temporal Cognitive State
        ↓
Meaningful Event
        ↓
Agent Context
        ↓
LLM Reasoning
        ↓
Tool Decision
        ↓
Policy Validation
        ↓
Action
        ↓
User Response
        ↓
Updated State
        ↓
Persistent History
        ↓
Analytics
        ↓
Personalization
        ↓
Future Agent Context
```

---

# 26. Recommended MVP

Start with:

1. Real-time attention estimation
2. Fatigue estimation
3. Distraction estimation
4. Temporal state estimation
5. Sustained attention-drop detection
6. Agentic break recommendation
7. User preference tracking
8. Intervention response tracking
9. Basic Focus Fingerprint
10. Privacy dashboard

Then add:

- Task-specific cognitive load
- Adaptive Workday
- Calendar integration
- Learned intervention effectiveness
- Advanced personalization
- Additional modes
- Productivity integrations

---

# 27. Recommended Deployment Architecture

For a college/mini-project MVP, avoid unnecessary microservices.

A practical deployment is:

```text
Frontend
   ↓
NGINX
   ↓
FastAPI
   ├── REST APIs
   ├── WebSocket
   ├── State/Event Engine
   └── Agent
         ├── LangGraph
         ├── LangChain
         └── LLM
   │
   ├── Redis
   └── MongoDB

DL Pipeline
   ├── OpenCV
   ├── MediaPipe
   └── PyTorch
```

Docker/Docker Compose can package the major services.

Kafka/RabbitMQ and a full microservice architecture are not necessary for the initial version.

---

# 28. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React / Next.js |
| Styling | Tailwind CSS |
| Camera | WebRTC |
| Realtime Events | WebSocket |
| API | FastAPI |
| API Gateway | NGINX |
| Computer Vision | OpenCV |
| Landmark Detection | MediaPipe |
| Deep Learning | PyTorch |
| Training | Google Colab |
| Hot State | Redis |
| Database | MongoDB |
| Agent Orchestration | LangGraph |
| Agent Components | LangChain |
| LLM | Configurable LLM API |
| Analytics | Python / Pandas / NumPy |
| ML Analytics | Scikit-learn where useful |
| Containers | Docker / Docker Compose |

---

# 29. Team Ownership

## Member 1 — Project Lead / Backend + Agent

Owns:

- FastAPI
- MongoDB
- Redis
- NGINX
- REST APIs
- WebSocket backend
- Authentication
- Session management
- State/event engine
- Context builder
- LangGraph
- LangChain
- LLM integration
- Agent tools
- Agent guardrails
- Final system integration

## Member 2 — Deep Learning / Computer Vision

Owns:

- Dataset
- OpenCV
- MediaPipe
- Feature engineering
- PyTorch
- Attention model
- Fatigue model
- Distraction model
- Cognitive-load model
- Model evaluation
- Inference packaging

## Member 3 — Frontend / Realtime UX

Owns:

- React/Next.js
- TypeScript
- UI/UX
- WebRTC client
- WebSocket client
- Dashboard
- Charts
- Intervention UI
- Focus Fingerprint UI
- Modes
- Privacy UI

## Member 4 — Analytics / Personalization

Owns:

- Focus Fingerprint
- Weekly analytics
- Intervention effectiveness
- Recovery analytics
- Personalization
- Task-specific cognitive-load analytics
- Adaptive Workday logic
- Historical insights

---

# 30. Parallel Development Contracts

The four members should not need to wait for one another.

### DL → Backend

```json
{
  "sessionId": "S456",
  "timestamp": "...",
  "attention": 0.72,
  "fatigue": 0.31,
  "distraction": 0.18,
  "cognitiveLoad": 0.54,
  "confidence": 0.91
}
```

### Backend → Agent

```json
{
  "currentState": {},
  "session": {},
  "userPreferences": {},
  "history": {}
}
```

### Agent → Backend

```json
{
  "action": "SUGGEST_BREAK",
  "type": "SHORT_WALK",
  "duration": 5,
  "reason": "Sustained attention decline"
}
```

### Backend → Frontend

```json
{
  "type": "INTERVENTION",
  "interventionId": "I789",
  "recommendation": {
    "type": "SHORT_WALK",
    "duration": 5
  }
}
```

### Analytics → Agent

```json
{
  "preferredIntervention": "SHORT_WALK",
  "acceptanceRate": 0.78,
  "peakFocusWindow": "10:00-12:00",
  "averageRecoveryTime": 8
}
```

---

# 31. Mock-First Development

Every subsystem should have a mock mode.

### DL

```text
mock_dl_prediction()
```

### Backend

```text
mock_session()
mock_user()
mock_history()
```

### Agent

```text
mock_agent_response()
```

### Analytics

```text
mock_historical_data()
```

### Frontend

Mock:

```text
REST responses
WebSocket events
Intervention events
State updates
```

This allows all four members to develop in parallel.

---

# 32. Git Strategy

Branches:

```text
main

feature/backend
feature/dl-pipeline
feature/frontend
feature/analytics
```

Workflow:

```text
Feature Branch
      ↓
Implementation
      ↓
Testing
      ↓
Commit
      ↓
Pull Request
      ↓
Review
      ↓
Merge
```

Do not directly push unfinished work to `main`.

---

# 33. Final Mental Model

```text
Member 2
PERCEPTION
"What is happening?"
       │
       ▼
Camera → CV → DL
       │
       ▼
Structured Signals
       │
       ▼
Member 1
STATE + AGENT
"What should we do?"
       │
       ▼
State → Event → Context
       │
       ▼
LangGraph → LLM → Tool
       │
       ▼
Validated Action
       │
       ▼
Member 3
EXPERIENCE
"How should the user see it?"
       │
       ▼
Frontend → Intervention
       │
       ▼
User Response
       │
       ▼
Member 4
ANALYTICS
"What can we learn?"
       │
       ▼
Focus Fingerprint
Personalization
Recovery Analytics
       │
       └──────────► Future Agent Context
```

---

# 34. Core Architectural Principles

1. **Do not send every webcam frame to the LLM.**
2. **Use temporal state before event detection.**
3. **Use events to trigger agent reasoning.**
4. **Keep raw media separate from structured cognitive signals.**
5. **Redis represents hot/current state.**
6. **MongoDB represents durable history.**
7. **WebRTC carries media.**
8. **WebSocket carries realtime application events.**
9. **REST handles normal request-response operations.**
10. **NGINX is the edge/reverse proxy, not business logic.**
11. **The LLM proposes; deterministic backend policy validates and executes.**
12. **Analytics should inform personalization without being confused with the agent itself.**
13. **Use stable contracts and mocks so team members can develop independently.**
14. **Do not store raw webcam video unless there is a specific, justified requirement.**

The overall system is:

> **Perception → State → Intelligence → Action → Experience → Learning**

This architecture gives FocusMirror a realistic combination of Deep Learning, Computer Vision, AI agents, backend engineering, real-time systems, analytics, personalization and privacy.
