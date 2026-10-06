# FocusMirror — Team Work Allocation & Responsibility Plan

## Project

**FocusMirror: Real-Time Cognitive Load & Attention Monitoring Using Deep Learning and AI Agents**

### Team Size
4 Members

### Development Philosophy

The project will be developed using four largely independent workstreams:

1. **Backend, Database & AI Agent Architecture**
2. **Deep Learning & Computer Vision**
3. **Frontend, WebRTC & User Experience**
4. **Analytics, Personalization & Product Intelligence**

Each member owns a complete subsystem.

The team will define stable interfaces/contracts between these subsystems so that development can happen **in parallel**.

---

# 1. Overall System Architecture

```text
                         ┌──────────────────────────┐
                         │        USER               │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │ React / Next.js Frontend  │
                         │ Member 3                  │
                         └───────┬─────────┬────────┘
                                 │         │
                    WebRTC Camera│         │REST / WebSocket
                                 │         │
                                 ▼         ▼
                        ┌────────────┐  ┌─────────────┐
                        │ DL / CV    │  │    NGINX    │
                        │ Pipeline   │  │ API Gateway │
                        │ Member 2   │  │  Member 1   │
                        └─────┬──────┘  └──────┬──────┘
                              │                │
                              │                ▼
                              │       ┌──────────────────┐
                              │       │     FastAPI      │
                              │       │    Backend       │
                              │       │    Member 1      │
                              │       └───────┬──────────┘
                              │               │
                              ▼               ▼
                     ┌────────────────┐  ┌──────────────┐
                     │ State / Events  │  │ Redis        │
                     │ Member 1       │  │ Current State│
                     └───────┬────────┘  └──────────────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │ AI Agent Brain         │
                  │ LangGraph + LangChain  │
                  │ LLM + Tools            │
                  │ Member 1               │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Analytics &            │
                  │ Personalization        │
                  │ Member 4               │
                  └───────────┬────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │ MongoDB        │
                     │ Persistent Data│
                     └────────────────┘


2. Team Ownership Summary
Member	Role	Primary Ownership
Member 1	Project Lead / Backend & AI Agent Architect	Backend, DB, APIs, NGINX, WebSockets, LangGraph, LangChain, LLM, Agent Tools
Member 2	Deep Learning & Computer Vision Engineer	Webcam processing, OpenCV, MediaPipe, PyTorch, attention/fatigue/cognitive-load models
Member 3	Frontend & Realtime UX Engineer	React/Next.js, UI, WebRTC client, WebSocket client, dashboards, visualizations
Member 4	Analytics & Personalization Engineer	Focus analytics, Focus Fingerprint, intervention effectiveness, personalization, reports, product intelligence


3. MEMBER 1 — PROJECT LEAD
Backend, Database & AI Agent Architect
Primary Responsibility
Member 1 owns the complete backend architecture and the complete AI-agent architecture.
This includes:
- Backend APIs
- Database
- Authentication
- Session management
- API gateway
- WebSockets
- Backend business logic
- Redis
- MongoDB
- LangChain
- LangGraph
- LLM integration
- Agent reasoning
- Agent tools
- Agent memory/context
- Agent policies/guardrails
- Integration of all subsystems
- Deployment architecture
The goal is that Member 1 owns the system backbone.
3.1 Backend Stack
Technologies
- Python
- FastAPI
- Pydantic
- NGINX
- Redis
- MongoDB
- PyMongo
- JWT
- WebSockets
- Docker
- Docker Compose
3.2 Backend API Development
Member 1 develops all application APIs.
Authentication APIs
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me

Responsibilities:
- User registration
- Password hashing
- JWT authentication
- Token validation
- Authentication middleware
- Authorization
3.3 Session APIs
POST /api/session/start
POST /api/session/end
GET  /api/session/current
GET  /api/session/{sessionId}
GET  /api/session/history

Responsibilities:
- Generate session IDs
- Initialize session state
- Store session metadata
- Track session duration
- End sessions
- Generate session summaries
3.4 Focus APIs
GET /api/focus/current
GET /api/focus/history
GET /api/focus/summary
GET /api/focus/fingerprint

These APIs expose processed focus information to the frontend.
3.5 User & Preference APIs
GET  /api/user/profile
PUT  /api/user/profile

GET  /api/preferences
PUT  /api/preferences

Preferences may include:
{
  "preferredBreakDuration": 5,
  "preferredIntervention": "SHORT_WALK",
  "notificationEnabled": true,
  "personalizationEnabled": true
}

3.6 Privacy APIs
GET    /api/privacy/settings
PUT    /api/privacy/settings
DELETE /api/privacy/history
DELETE /api/privacy/session/{sessionId}

Features:
- Disable personalization
- Disable camera processing
- Delete session history
- Delete user history
- Privacy settings
3.7 WebSocket Backend
Member 1 owns the complete WebSocket backend.
Example:
/ws/session/{sessionId}

The WebSocket handles realtime application events.
Backend → Frontend
STATE_UPDATE
FOCUS_ALERT
INTERVENTION
AGENT_MESSAGE
SESSION_END

Frontend → Backend
INTERVENTION_RESPONSE
USER_ACTION
SESSION_CONTROL
ACKNOWLEDGEMENT

Important:
WebSocket is not used for raw webcam video.
WebRTC handles media.
3.8 API Gateway
Member 1 owns NGINX.
Example:
Frontend
    ↓
NGINX
    ↓
FastAPI

NGINX responsibilities:
- Reverse proxy
- API routing
- WebSocket proxying
- HTTPS termination
- Rate limiting
- Static file serving if required
- Load balancing if required
Example routing:
/api/auth/*       → FastAPI
/api/session/*    → FastAPI
/api/focus/*      → FastAPI
/api/user/*       → FastAPI
/api/privacy/*    → FastAPI
/api/agent/*      → FastAPI
/ws/*             → FastAPI WebSocket

3.9 Redis
Member 1 owns Redis.
Redis represents:
What is happening RIGHT NOW?

Example:
session:S456:state

Possible state:
{
  "attention": 0.38,
  "fatigue": 0.76,
  "distraction": 0.71,
  "cognitiveLoad": 0.54,
  "attentionTrend": "DECLINING",
  "lowAttentionDuration": 180,
  "lastIntervention": "NOTIFICATION"
}

Redis responsibilities:
- Current session state
- Agent working state
- Temporary state
- Event information
- TTL
- Rate limiting
- Cooldowns
- Optional Redis Streams
3.10 MongoDB
Member 1 owns the complete MongoDB architecture.
Collections:
users
sessions
events
interventions
reports
agent_logs
focus_profiles
preferences
analytics

MongoDB stores:
- User profile
- Preferences
- Session history
- Important events
- Intervention history
- Agent decisions
- Focus Fingerprint
- Analytics
- Reports
Raw webcam frames should NOT be stored by default.
3.11 AI Agent — COMPLETE OWNERSHIP
Member 1 also owns the complete agent architecture.
This is an important distinction:
The Deep Learning member builds the perception system.
Member 1 builds the decision-making system.
3.12 LangGraph
Member 1 designs the agent workflow using LangGraph.
Example:
             EVENT
               │
               ▼
        Context Builder
               │
               ▼
          Agent State
               │
               ▼
          LLM Reasoning
               │
               ▼
        Action Selection
               │
               ▼
          Policy Check
          /          \
      BLOCK          ALLOW
        │              │
        │              ▼
        │            Tool
        │              │
        │              ▼
        │          Tool Result
        │              │
        └───────► State Update
                       │
                       ▼
                     END

3.13 Agent Context Builder
The agent receives structured information.
Example:
{
  "currentState": {
    "attention": 0.32,
    "fatigue": 0.78,
    "distraction": 0.71,
    "lowAttentionDuration": 180
  },

  "session": {
    "duration": 5400,
    "lastIntervention": "30 minutes ago"
  },

  "preferences": {
    "preferredBreakDuration": 5,
    "preferredIntervention": "SHORT_WALK"
  },

  "history": {
    "shortWalkAcceptanceRate": 0.78
  }
}

The agent does NOT receive raw webcam frames.
3.14 LangChain
Member 1 owns:
- Prompt templates
- LLM integration
- Structured output
- Tool calling
- Context formatting
- Agent messages
- Retrieval components if required
3.15 Agent Tools
Member 1 develops the tool interface.
Example tools:
send_notification()
suggest_break()
suggest_walk()
start_focus_timer()
generate_focus_summary()
retrieve_user_history()
retrieve_focus_profile()
update_session_state()

Every tool should have:
- Input schema
- Output schema
- Validation
- Error handling
- Authorization
3.16 Agent Guardrails
The LLM should NOT directly execute arbitrary operations.
Architecture:
LLM
 ↓
Tool Proposal
 ↓
Policy / Guardrail
 ↓
Validation
 ↓
Tool Execution

Example:
Agent chooses:

send_notification()

↓

Backend checks:

Is notification allowed?
Is cooldown active?
Has user disabled notifications?
Has intervention already been sent recently?

↓

ALLOW / BLOCK

3.17 Agent Features
Member 1 owns:
Intelligent Break Recommendation
Attention declining
+
Fatigue increasing
+
Long continuous session
        ↓
Agent
        ↓
Recommend break

Adaptive Intervention
The agent considers:
- Current state
- User preferences
- Previous intervention responses
- Session duration
- Intervention cooldown
Agent Explanations
Example:
"You've been working continuously for 52 minutes and your attention has been declining for the last 3 minutes. A 5-minute walk may help you recover."

3.18 Member 1 Final Deliverables
By the end, Member 1 should have:
- FastAPI backend
- Authentication
- Session APIs
- Focus APIs
- User APIs
- Privacy APIs
- NGINX configuration
- Redis architecture
- MongoDB architecture
- WebSocket server
- Agent service
- LangChain implementation
- LangGraph implementation
- LLM integration
- Tool system
- Agent guardrails
- Backend tests
- API documentation
- Docker setup
- Final system integration
4. MEMBER 2 — DEEP LEARNING & COMPUTER VISION ENGINEER
Primary Responsibility
Member 2 owns everything related to:
"What is happening to the user?"

This person does NOT own the backend database or agent reasoning.
4.1 Technology Stack
- Python
- OpenCV
- MediaPipe
- PyTorch
- NumPy
- Pandas
- Scikit-learn
- Google Colab
4.2 Dataset & Research
Responsibilities:
- Find datasets
- Clean datasets
- Preprocess data
- Feature engineering
- Label analysis
- Train/validation/test split
- Data augmentation
- Dataset documentation
4.3 Computer Vision Pipeline
Pipeline:
Camera
 ↓
Frame
 ↓
OpenCV
 ↓
MediaPipe
 ↓
Landmarks
 ↓
Feature Extraction
 ↓
PyTorch Model
 ↓
Predictions

4.4 OpenCV
Responsibilities:
- Frame preprocessing
- Resize
- Crop
- Normalize
- Frame sampling
- Image quality checks
- Face region extraction
4.5 MediaPipe
Extract:
- Face landmarks
- Eye landmarks
- Head orientation
- Blink information
- Facial geometry
- Pose information where required
4.6 Feature Extraction
Possible features:
Eye Aspect Ratio
Blink Rate
Head Pose
Gaze Direction
Eye Closure Duration
Face Orientation
Movement
Posture

4.7 PyTorch Models
Member 2 builds models for:
Attention Estimation
Output:
{
  "attention": 0.72,
  "confidence": 0.91
}

Fatigue Estimation
{
  "fatigue": 0.31
}

Distraction Detection
{
  "distraction": 0.18
}

Cognitive Load
{
  "cognitiveLoad": 0.54
}

4.8 Model Evaluation
Member 2 owns:
- Accuracy
- Precision
- Recall
- F1
- ROC-AUC where applicable
- Confusion matrix
- Inference latency
- Robustness testing
Test conditions:
- Different lighting
- Glasses
- Different camera positions
- Head movement
- Different users
- Partial occlusion
4.9 Temporal Prediction Output
Member 2 should NOT send raw frames to the backend.
Instead, produce structured predictions.
Example:
{
  "sessionId": "S456",
  "timestamp": "2026-09-18T10:30:00Z",
  "attention": 0.72,
  "fatigue": 0.31,
  "distraction": 0.18,
  "cognitiveLoad": 0.54,
  "confidence": 0.91
}

This becomes the official:
DL → Backend Contract

4.10 Inference Module
Member 2 must package the trained model so that it can be called independently.
Example:
result = model.predict(frame)


Expected output:
{    "attention": 0.72,    "fatigue": 0.31,    "distraction": 0.18,    "cognitive_load": 0.54,    "confidence": 0.91}


4.11 Mock Mode
Member 2 must also provide a mock inference mode.
Example:
mock_prediction()

This allows the backend and frontend to develop without waiting for the real model.
Example:
{
  "attention": 0.35,
  "fatigue": 0.75,
  "distraction": 0.65,
  "cognitiveLoad": 0.60
}

This is extremely important for parallel development.
4.12 Member 2 Final Deliverables
- Dataset pipeline
- Feature extraction
- OpenCV module
- MediaPipe module
- PyTorch model
- Training notebooks
- Evaluation report
- Inference module
- Model weights
- DL API/contract
- Mock inference module
- Documentation
- Latency benchmark
5. MEMBER 3 — FRONTEND & REALTIME UX ENGINEER
Primary Responsibility
Member 3 owns everything the user sees and interacts with.
The person owns:
- Frontend
- UI
- UX
- WebRTC client
- WebSocket client
- REST client
- Dashboard
- Visualizations
- Focus controls
5.1 Technology Stack
- React / Next.js
- TypeScript
- Tailwind CSS
- WebRTC
- WebSocket
- REST APIs
- Recharts or equivalent
5.2 Authentication UI
Build:
Login
Register
Logout
Profile

The frontend should communicate with the backend APIs through the predefined API contract.
5.3 Main Dashboard
Dashboard should display:
Current Attention
Fatigue
Distraction
Cognitive Load
Session Duration
Current Mode

Example:
Attention       ███████░░░ 72%

Fatigue         ███░░░░░░░ 31%

Distraction     ██░░░░░░░░ 18%

Cognitive Load  █████░░░░░ 54%

5.4 Realtime Camera UI
Member 3 owns:
- Camera permission
- Camera preview
- Start/stop camera
- WebRTC client
- Camera status
- Camera error handling
Important:
Member 3 does NOT need to implement the ML model.
5.5 WebRTC
Frontend establishes the media connection.
Conceptually:
Browser Camera
      ↓
WebRTC
      ↓
Inference Pipeline

The frontend team only owns the browser-side WebRTC implementation.
5.6 WebSocket Client
Member 3 implements the WebSocket client.
Example:
/ws/session/{sessionId}

The frontend listens for:
STATE_UPDATE
FOCUS_ALERT
INTERVENTION
AGENT_MESSAGE
SESSION_END

5.7 Intervention UI
Example:
┌──────────────────────────────┐
│       FocusMirror            │
│                              │
│ Your attention is declining. │
│                              │
│ A 5-minute walk may help.    │
│                              │
│ [Take Break] [Dismiss]       │
└──────────────────────────────┘

User response goes back through WebSocket.
5.8 Focus Fingerprint UI
Display:
FOCUS FINGERPRINT

Peak Focus
10:00 AM – 12:00 PM

Average Focus
47 minutes

Recovery Time
8 minutes

Best Task
Coding

Frequent Drop
2:30 PM – 4:00 PM

5.9 Session Analytics
Build:
- Attention timeline
- Fatigue timeline
- Cognitive load graph
- Distraction graph
- Intervention timeline
- Session summary
5.10 FocusMirror Modes
Frontend UI for:
Study
Deep Work
Work
Meeting
Vigilance
Custom

Mode selection is sent to backend.
5.11 Privacy Dashboard
UI for:
Camera Processing     ON/OFF
Personalization       ON/OFF
History Storage       ON/OFF

Also show:
Raw video stored: NO
Face identification: OFF
Cloud video upload: OFF

5.12 Member 3 Final Deliverables
- Complete frontend
- Login/Register
- Dashboard
- Camera interface
- WebRTC client
- WebSocket client
- Focus visualizations
- Intervention UI
- Focus Fingerprint UI
- Session history UI
- Mode selector
- Privacy dashboard
- Responsive design
- Frontend tests
- UI documentation
6. MEMBER 4 — ANALYTICS & PERSONALIZATION ENGINEER
Primary Responsibility
Member 4 owns:
"What does the system learn about the user's behavior over time?"

This member does NOT own the LLM brain.
The agent itself belongs to Member 1.
Member 4 instead develops the analytics, personalization and intelligence modules that the agent can consume.
This creates a clean separation:
Member 4
Analytics / Personalization
          ↓
Structured Context
          ↓
Member 1
AI Agent

6.1 Technology Stack
- Python
- Pandas
- NumPy
- Scikit-learn
- Pydantic
- MongoDB data schemas/contracts
- Statistical analysis
- Optional lightweight ML
6.2 Focus Fingerprint
Member 4 builds the logic for calculating the user's Focus Fingerprint.
Inputs:
Session History
Attention History
Task Type
Time of Day
Fatigue
Cognitive Load
Interventions
Recovery

Output:
{
  "peakFocusWindow": "10:00-12:00",
  "averageContinuousFocus": 47,
  "averageRecoveryTime": 8,
  "bestTaskType": "CODING",
  "frequentDropWindow": "14:30-16:00"
}

6.3 Weekly Insights
Generate structured insights.
Example:
Your strongest focus period is between
10 AM and 12 PM.

Your attention drops more frequently
after 50 minutes of continuous work.

Short walks have been more effective
than notifications for recovery.

Important:
Member 4 generates the underlying analytics.
Member 1's agent can later turn these into natural-language recommendations.
6.4 Intervention Effectiveness
Track:
Before intervention
        ↓
Intervention
        ↓
After intervention

Example:
Attention Before = 0.38

Intervention = SHORT_WALK

Attention After = 0.71

Calculate:
Recovery Improvement
Acceptance Rate
Average Recovery Time
Intervention Effectiveness

6.5 Personalization Engine
Determine user preferences based on historical behavior.
Example:
SHORT_WALK
Acceptance = 78%

COFFEE_BREAK
Acceptance = 61%

BREATHING
Acceptance = 43%

Output:
{
  "preferredIntervention": "SHORT_WALK",
  "acceptanceRate": 0.78
}

This information can be consumed by the AI agent.
6.6 Task-Specific Cognitive Load
Member 4 develops analytics around:
Task Type
+
Attention
+
Cognitive Load
+
Fatigue
+
Duration

Example:
Task	Average Load
Documentation	Low
Coding	Medium
Debugging	High
Meetings	Medium
Data Analysis	High


Initially, task type can be selected manually.
Future versions may use:
- Calendar
- IDE context
- Browser context
- Task management systems
6.7 Adaptive Workday Intelligence
Member 4 develops the scheduling logic.
Inputs:
Focus Fingerprint
+
Current Attention
+
Task Complexity
+
Calendar
+
User Preferences

Example:
Peak Focus:
10 AM – 12 PM

High Complexity Task:
Debugging

Current Schedule:
Debugging at 3 PM

Recommendation:
"Your strongest focus period is 10 AM–12 PM. Would you like to move the debugging task to your morning focus window?"

Member 4 develops the underlying recommendation logic.
Member 1 exposes it through the agent.
Member 3 displays it.
6.8 Analytics API Contract
Member 4 should expose analytics through clean Python functions/modules.
Example:
calculate_focus_fingerprint(session_history)calculate_intervention_effectiveness(interventions)calculate_recovery_time(session)calculate_attention_trends(session_history)generate_weekly_insights(session_history)get_personalized_interventions(user_history)calculate_task_cognitive_load(task_history)


These should be callable independently.
6.9 Mock Dataset
Member 4 must create synthetic/mock historical data.
Example:
mock_sessions.json
mock_interventions.json
mock_user_history.json

This allows analytics development before the real database is populated.
6.10 Member 4 Final Deliverables
- Focus Fingerprint engine
- Attention trend analytics
- Weekly insights
- Intervention effectiveness
- Recovery analytics
- Personalization engine
- Task-specific cognitive-load analytics
- Adaptive Workday recommendation logic
- Mock historical dataset
- Analytics contracts
- Unit tests
- Documentation
7. CRITICAL PARALLEL DEVELOPMENT STRATEGY
The project must NOT be developed sequentially.
The four members should be able to work simultaneously.
7.1 Contract-First Development
Before implementation, define contracts.
DL → Backend
{
  "sessionId": "S456",
  "timestamp": "2026-09-18T10:30:00Z",
  "attention": 0.72,
  "fatigue": 0.31,
  "distraction": 0.18,
  "cognitiveLoad": 0.54,
  "confidence": 0.91
}

Member 2 can build against this.
Member 1 can build against this.
Neither needs to wait for the other.
7.2 Backend → Agent
{
  "currentState": {},
  "session": {},
  "userPreferences": {},
  "history": {}
}

Member 1 owns this contract.
7.3 Agent → Backend
{
  "action": "SUGGEST_BREAK",
  "type": "SHORT_WALK",
  "duration": 5,
  "reason": "Sustained attention decline"
}

7.4 Backend → Frontend
WebSocket:
{
  "type": "INTERVENTION",
  "interventionId": "I789",
  "recommendation": {
    "type": "SHORT_WALK",
    "duration": 5
  }
}

Member 3 can build the UI using mock WebSocket messages.
7.5 Analytics → Agent
{
  "preferredIntervention": "SHORT_WALK",
  "shortWalkAcceptanceRate": 0.78,
  "peakFocusWindow": "10:00-12:00",
  "averageRecoveryTime": 8
}

Member 4 can develop this using mock historical data.
Member 1 can integrate it later.
8. MOCK-FIRST DEVELOPMENT
Every subsystem must have a mock mode.
DL Mock
mock_dl_prediction()

Backend Mock
mock_session()
mock_user()
mock_history()

Agent Mock
mock_agent_response()

Analytics Mock
mock_historical_data()

Frontend Mock
mock WebSocket events
mock REST responses
mock intervention events

This ensures nobody is blocked.
9. DEVELOPMENT PHASES
Phase 1 — Foundation
Member 1
- FastAPI
- MongoDB
- Redis
- Authentication
- Session APIs
- API contracts
Member 2
- Dataset
- MediaPipe
- OpenCV
- Feature extraction
- Baseline model
Member 3
- Next.js/React
- Login
- Dashboard skeleton
- Component system
Member 4
- Mock historical dataset
- Focus Fingerprint algorithm
- Analytics functions
All four work simultaneously.
10. PHASE 2 — Core Subsystems
Member 1
FastAPI
+
Redis
+
MongoDB
+
WebSocket
+
NGINX

Member 2
Camera
↓
OpenCV
↓
MediaPipe
↓
PyTorch

Member 3
Camera UI
+
WebRTC
+
Dashboard
+
WebSocket Client

Member 4
Focus Fingerprint
+
Intervention Analytics
+
Personalization

11. PHASE 3 — AI Agent
Member 1 develops:
Event
 ↓
Context
 ↓
LangGraph
 ↓
LLM
 ↓
Tool Selection
 ↓
Policy
 ↓
Action

Member 4 provides structured personalization data.
Member 2 provides model output.
Member 3 provides the UI.
12. PHASE 4 — Integration
Final pipeline:
                 CAMERA
                    │
                    ▼
              WebRTC Client
                    │
                    ▼
            OpenCV + MediaPipe
                    │
                    ▼
                 PyTorch
                    │
                    ▼
            DL Predictions
                    │
                    ▼
            State Estimator
                    │
                    ▼
                  Redis
                    │
                    ▼
             Event Detection
                    │
                    ▼
              Context Builder
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
             Policy / Guardrail
                    │
                    ▼
                 Action
                    │
                    ▼
                WebSocket
                    │
                    ▼
                Frontend
                    │
                    ▼
              User Response
                    │
                    ▼
               Redis/MongoDB
                    │
                    ▼
              Analytics Engine
                    │
                    ▼
             Personalization
                    │
                    └──────────────► Agent

13. GIT BRANCH STRUCTURE
main
│
├── feature/backend
├── feature/dl-pipeline
├── feature/frontend
└── feature/analytics

13.1 Member 1
Owns:
feature/backend

Includes:
backend/
api/
agent/
database/
nginx/
websocket/

13.2 Member 2
Owns:
feature/dl-pipeline

Includes:
ml/
cv/
models/
training/
inference/

13.3 Member 3
Owns:
feature/frontend

Includes:
frontend/
components/
pages/
hooks/
websocket-client/
webrtc/

13.4 Member 4
Owns:
feature/analytics

Includes:
analytics/
personalization/
reports/
focus_fingerprint/
datasets/

14. GIT RULES
Nobody directly pushes unfinished work to main.
Workflow:
Create feature branch
        ↓
Implement
        ↓
Test
        ↓
Commit
        ↓
Push
        ↓
Pull Request
        ↓
Review
        ↓
Merge

Commit examples:
feat: add session management API
feat: add attention inference pipeline
feat: add focus dashboard
feat: add intervention effectiveness analytics

15. FINAL OWNERSHIP MATRIX
Component	M1	M2	M3	M4
FastAPI	OWNER			
MongoDB	OWNER			
Redis	OWNER			
NGINX	OWNER			
REST APIs	OWNER			
WebSocket Backend	OWNER			
Authentication	OWNER			
Session Management	OWNER			
LangGraph	OWNER			
LangChain	OWNER			
LLM Integration	OWNER			
Agent Tools	OWNER			
Agent Guardrails	OWNER			
OpenCV		OWNER		
MediaPipe		OWNER		
PyTorch		OWNER		
Model Training		OWNER		
Model Evaluation		OWNER		
WebRTC Client			OWNER	
React/Next.js			OWNER	
Dashboard			OWNER	
UI/UX			OWNER	
WebSocket Client			OWNER	
Focus Fingerprint Logic				OWNER
Weekly Analytics				OWNER
Intervention Analytics				OWNER
Personalization				OWNER
Adaptive Workday Logic				OWNER
Task Cognitive Load Analytics				OWNER


16. RESPONSIBILITY BOUNDARIES
Member 1 DOES NOT own
- PyTorch model development
- Computer vision research
- Frontend UI
- React components
- Analytics algorithm development
Member 2 DOES NOT own
- FastAPI
- MongoDB
- Redis
- LangGraph
- Frontend
- Agent reasoning
Member 3 DOES NOT own
- PyTorch
- MongoDB
- LangGraph
- Backend business logic
- Analytics algorithms
Member 4 DOES NOT own
- Core LLM reasoning
- LangGraph orchestration
- FastAPI infrastructure
- PyTorch perception models
- Frontend implementation
17. MOST IMPORTANT ARCHITECTURAL RULE
The team should maintain this separation:
MEMBER 2
"What is happening?"
       │
       ▼
DL / Computer Vision
       │
       ▼
Structured State
       │
       ▼
MEMBER 1
"What should the system do?"
       │
       ▼
AI Agent
       │
       ▼
Action
       │
       ▼
MEMBER 3
"How should the user experience it?"
       │
       ▼
Frontend
       │
       ▼
MEMBER 4
"What can we learn from the user's history?"
       │
       ▼
Analytics / Personalization
       │
       └──────────────► MEMBER 1 AGENT

18. FINAL TEAM MENTAL MODEL
Member 1 — THE BACKBONE
Owns the system infrastructure and the AI brain.

Backend + Database + APIs + NGINX + WebSockets + LangGraph + LangChain + LLM + Tools + Guardrails.
Member 2 — THE EYES
Owns perception.

Camera + OpenCV + MediaPipe + PyTorch + Attention + Fatigue + Distraction + Cognitive Load.
Member 3 — THE FACE
Owns the user experience.

React/Next.js + WebRTC + WebSocket Client + Dashboard + Visualizations + Intervention UI + Privacy UI.
Member 4 — THE MEMORY & ANALYTICS
Owns behavioral intelligence.

Focus Fingerprint + Historical Analytics + Intervention Effectiveness + Personalization + Adaptive Workday + Task Analytics.
19. FINAL END-TO-END OWNERSHIP
                    USER
                     │
                     ▼
             ┌───────────────┐
             │ MEMBER 3      │
             │ FRONTEND      │
             └───────┬───────┘
                     │
                  WebRTC
                     │
                     ▼
             ┌───────────────┐
             │ MEMBER 2      │
             │ DL / CV       │
             └───────┬───────┘
                     │
               Predictions
                     │
                     ▼
             ┌───────────────┐
             │ MEMBER 1      │
             │ BACKEND       │
             │ + AGENT BRAIN  │
             └───────┬───────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
        Redis/Mongo       LangGraph
                              │
                              ▼
                             LLM
                              │
                              ▼
                           Tools
                              │
                              ▼
                         WebSocket
                              │
                              ▼
                         MEMBER 3
                         FRONTEND
                              │
                              ▼
                           USER
                              │
                              ▼
                       User Behaviour
                              │
                              ▼
                      ┌───────────────┐
                      │ MEMBER 4      │
                      │ ANALYTICS     │
                      │ PERSONALIZE   │
                      └───────┬───────┘
                              │
                              ▼
                       Agent Context
                              │
                              └────────► MEMBER 1

20. SUCCESS CRITERIA
The project is considered fully integrated when:
- [ ] User can register/login
- [ ] User can start a focus session
- [ ] Browser camera works
- [ ] WebRTC connection works
- [ ] DL pipeline generates predictions
- [ ] Backend receives structured predictions
- [ ] Redis maintains current state
- [ ] Event engine detects sustained attention drops
- [ ] MongoDB stores session/event data
- [ ] Agent receives structured context
- [ ] LangGraph executes agent workflow
- [ ] LLM selects an appropriate tool
- [ ] Guardrail validates the action
- [ ] Tool executes
- [ ] WebSocket sends intervention to frontend
- [ ] User can accept/dismiss intervention
- [ ] Response is stored
- [ ] Intervention effectiveness is calculated
- [ ] Focus Fingerprint is generated
- [ ] Personalization influences future recommendations
- [ ] Privacy controls work
- [ ] Session summary is generated
- [ ] Complete system works end-to-end
FINAL PRINCIPLE
The team should never think:
"I'll finish my part and then the next person can start."

Instead:
"I'll define and implement my subsystem against a stable contract while everyone else develops against the same contract."

That is what allows all four members to work in parallel.
The final architecture should maintain this separation:
Perception → State → Intelligence → Action → Experience → Learning
Where:
- Member 2 owns Perception
- Member 1 owns State + Intelligence + Action infrastructure
- Member 3 owns Experience
- Member 4 owns Learning/Analytics
And the Project Lead (Member 1) owns the final integration of the entire system.