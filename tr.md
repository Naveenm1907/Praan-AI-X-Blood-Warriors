# PRAAN AI — Technical Requirements

> FastAPI Backend × Next.js Frontend × AWS Cloud
> Aligned with Hackathon 5-Layer Recommended Stack

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: FULL STACK (User Interaction)                          │
│                                                                   │
│  ┌─────────────────────┐         ┌──────────────────────────┐   │
│  │  FRONTEND            │         │  BACKEND                  │   │
│  │  Next.js 14          │◄───────►│  Python 3.11 + FastAPI    │   │
│  │  React + Tailwind    │  REST   │  Uvicorn ASGI Server      │   │
│  │  App Router          │         │  Pydantic Models           │   │
│  └─────────────────────┘         └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: DATA ENGINEERING (Pipelines & Storage)                 │
│                                                                   │
│  ┌──────────┐  ┌─────────┐  ┌─────┐  ┌─────────┐  ┌────────┐  │
│  │ DynamoDB │  │   S3    │  │ RDS │  │ Kinesis │  │  Glue  │  │
│  │ NoSQL    │  │ Files   │  │ SQL │  │ Streams │  │  ETL   │  │
│  └──────────┘  └─────────┘  └─────┘  └─────────┘  └────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: DATA SCIENCE & AI (Intelligence)                       │
│                                                                   │
│  ┌──────────┐  ┌─────────┐  ┌───────┐  ┌──────────┐           │
│  │SageMaker │  │ Bedrock │  │ Textract│ │Feature   │           │
│  │  ML      │  │  LLM    │  │  OCR   │ │ Store    │           │
│  └──────────┘  └─────────┘  └───────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: AUTOMATION (Orchestration)                             │
│                                                                   │
│  ┌──────────┐  ┌─────────────┐  ┌────────────┐  ┌────────┐   │
│  │ Lambda   │  │ API Gateway │  │EventBridge │  │  SQS   │   │
│  │ Functions│  │  REST APIs  │  │  Events    │  │ Queue  │   │
│  └──────────┘  └─────────────┘  └────────────┘  └────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 5: DEPLOYMENT & MONITORING                                │
│                                                                   │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌──────────┐    │
│  │CloudWatch│  │   X-Ray    │  │  WAF     │  │ App      │    │
│  │  Logs    │  │  Tracing   │  │Security  │  │ Runner   │    │
│  └──────────┘  └────────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## FastAPI Backend Architecture

### Entry Point: `main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import patient, blood_bank, donor, voice, workflow

app = FastAPI(title="PRAAN AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router, prefix="/api")
app.include_router(blood_bank.router, prefix="/api")
app.include_router(donor.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
```

### Config: `config.py`
```python
import os
from enum import Enum

class Mode(str, Enum):
    MOCK = "mock"
    AWS = "aws"

APP_MODE = Mode(os.getenv("APP_MODE", "mock"))
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "praan")
```

---

## API Endpoints Specification

### Patient Module (`/api/patient`)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/patient` | Create patient | `{name, age, blood_group, location, lat, lng}` | Patient object |
| GET | `/patient/{id}` | Get patient details | path: id | Patient + urgency |
| POST | `/patient/{id}/report` | Upload medical report | multipart: file | OCR results |
| GET | `/patient/{id}/urgency` | Get urgency window | path: id | `{days_remaining, priority}` |
| GET | `/patient` | List all patients | query: status | Patient array |

### Blood Bank Module (`/api/blood-bank`)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/blood-bank` | List all inventory | - | BloodBank array |
| GET | `/blood-bank/search` | Search by criteria | query: blood_group, district | Filtered array |
| POST | `/blood-bank/reserve` | Reserve units | `{bank_id, blood_group, units}` | Reservation |
| POST | `/blood-bank/release` | Release reservation | `{reservation_id}` | Updated stock |
| GET | `/blood-bank/expiry` | Get expiring stock | query: days | Alert array |
| POST | `/blood-bank/seed` | Load seed data | - | Success message |

### Donor Module (`/api/donor`)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/donor/rank` | Rank donors for patient | query: patient_id | Ranked donor array |
| POST | `/donor/match` | Match donors to request | `{blood_group, location, count}` | Matched donors |
| GET | `/donor/{id}` | Get donor details | path: id | Donor object |
| GET | `/donor/{id}/history` | Donation history | path: id | History array |
| POST | `/donor/seed` | Load seed donors | - | Success message |

### Voice Call Module (`/api/voice`)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/voice/campaign` | Start parallel calls | `{donor_ids[], patient_id, language}` | Campaign object |
| GET | `/voice/campaign/{id}` | Get campaign status | path: id | Status + responses |
| POST | `/voice/response` | Record donor response | `{campaign_id, donor_id, response}` | Updated status |
| POST | `/voice/cancel` | Cancel remaining calls | `{campaign_id}` | Cancelled count |
| GET | `/voice/script` | Get call script | query: language, blood_group | Script text |

### Workflow Module (`/api/workflow`)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/workflow/start` | Start patient workflow | `{patient_id, units_needed}` | Workflow object |
| GET | `/workflow/{id}` | Get workflow status | path: id | Full timeline |
| GET | `/workflow/insights` | Failure learning data | - | Insights array |
| GET | `/workflow/active` | Active workflows | - | Workflow array |

---

## DynamoDB Table Schemas

### Table: `praan_patients`
```json
{
  "TableName": "praan_patients",
  "KeySchema": [
    {"AttributeName": "patient_id", "KeyType": "HASH"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "patient_id", "AttributeType": "S"},
    {"AttributeName": "blood_group", "AttributeType": "S"}
  ],
  "GlobalSecondaryIndexes": [{
    "IndexName": "blood_group_index",
    "KeySchema": [{"AttributeName": "blood_group", "KeyType": "HASH"}]
  }]
}
```

**Fields**: patient_id, name, age, blood_group, location, latitude, longitude, last_transfusion_date, cycle_length_days, hb_level, ferritin_level, mcv_level, urgency_window_days, consent_given, created_at

### Table: `praan_blood_banks`
```json
{
  "TableName": "praan_blood_banks",
  "KeySchema": [
    {"AttributeName": "bank_id", "KeyType": "HASH"}
  ]
}
```

**Fields**: bank_id, name, district, state, latitude, longitude, inventory (map: blood_group → {units_available, expiry_date, reserved_count}), contact_phone, last_updated

### Table: `praan_donors`
```json
{
  "TableName": "praan_donors",
  "KeySchema": [
    {"AttributeName": "donor_id", "KeyType": "HASH"}
  ],
  "GlobalSecondaryIndexes": [{
    "IndexName": "blood_group_index",
    "KeySchema": [{"AttributeName": "blood_group", "KeyType": "HASH"}]
  }]
}
```

**Fields**: donor_id, name, blood_group, phone, language, location, latitude, longitude, last_donation_date, total_donations, total_calls, calls_to_donations_ratio, eligibility_status, expected_next_transfusion_date, readiness_score

### Table: `praan_call_campaigns`
```json
{
  "TableName": "praan_call_campaigns",
  "KeySchema": [
    {"AttributeName": "campaign_id", "KeyType": "HASH"}
  ]
}
```

**Fields**: campaign_id, patient_id, donor_ids (list), status, responses (map: donor_id → {status, timestamp, retry_count}), language, started_at, completed_at, confirmed_count, target_count

### Table: `praan_workflows`
```json
{
  "TableName": "praan_workflows",
  "KeySchema": [
    {"AttributeName": "workflow_id", "KeyType": "HASH"}
  ]
}
```

**Fields**: workflow_id, patient_id, steps (list of {step_name, status, started_at, completed_at, details}), current_step, blood_bank_result, campaign_id, created_at, completed_at

---

## AWS Service Mapping

| Feature | AWS Service | Purpose |
|---------|------------|---------|
| Data storage | **DynamoDB** | All tables (patients, donors, blood banks, campaigns, workflows) |
| File storage | **S3** | Medical report uploads |
| OCR | **Textract** | Extract Hb, MCV, ferritin from medical reports |
| AI chat | **Bedrock** | Conversational AI with memory, multilingual |
| Voice calls | **Amazon Connect** | Outbound call campaigns (20 parallel) |
| Speech | **Polly** | Text-to-speech in 6 languages |
| Voice AI | **Lex** | Understand donor voice responses |
| ML | **SageMaker** | Urgency window prediction, donor readiness scoring |
| ML features | **Feature Store** | Store donor features for model training |
| Notifications | **SNS** | SMS fallback when voice call fails |
| Queue | **SQS** | Buffer workflow events |
| Events | **EventBridge** | Trigger scheduled workflows, expiry alerts |
| Functions | **Lambda** | Deploy FastAPI handler, event processors |
| API | **API Gateway** | REST API frontend |
| Streaming | **Kinesis** | Real-time event stream to dashboard |
| Auth | **Cognito** | User authentication |
| CDN | **CloudFront** | Frontend static asset delivery |
| Hosting | **Amplify** | Next.js frontend deployment |
| Runner | **App Runner** | FastAPI container deployment |
| Logs | **CloudWatch** | Application logging + metrics |
| Tracing | **X-Ray** | Distributed request tracing |
| Security | **WAF** | Web application firewall |
| Secrets | **Secrets Manager** | API keys, DB credentials |

---

## Security & Compliance

### DISHA Compliance (Digital Information Security in Healthcare Act)
- Patient consent required before any data processing
- Medical report data encrypted at rest (DynamoDB encryption) and in transit (HTTPS)
- Consent withdrawal API: patient can revoke data access at any time
- Data retention policy: medical reports auto-deleted after 90 days

### Authentication
- Cognito User Pools for patient/donor login
- API Gateway authorizer validates JWT tokens
- Admin dashboard requires coordinator role (Cognito Groups)

### Data Protection
- All API endpoints behind WAF
- Secrets (AWS keys, API keys) in Secrets Manager
- No PII in CloudWatch logs (masked)
- CORS restricted to frontend domain

### Consent Management
- Every patient record has `consent_given` boolean
- Donor outreach checks consent before calling
- Consent audit trail in DynamoDB stream

---

## Deployment Architecture

### Local Development
```
Frontend: npm run dev          → localhost:3000 (Next.js)
Backend:  uvicorn main:app     → localhost:8000 (FastAPI)
Mode:     APP_MODE=mock        → Uses seed data, no AWS calls
```

### Hackathon Demo Deployment
```
Frontend → Amplify (auto-deploy from GitHub)
Backend  → App Runner (containerized FastAPI)
Data     → DynamoDB (ap-south-1)
AI       → Bedrock + SageMaker endpoints
Voice    → Amazon Connect instance
```

### Environment Variables
```
APP_MODE=mock|aws
AWS_REGION=ap-south-1
DYNAMODB_TABLE_PREFIX=praan
COGNITO_USER_POOL_ID=
COGNITO_CLIENT_ID=
S3_BUCKET_NAME=praan-medical-reports
CONNECT_INSTANCE_ID=
POLLY_VOICE_ID=Aditi
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Blood bank search | < 500ms |
| Donor ranking (20 donors) | < 1 second |
| Urgency window calculation | < 200ms |
| Voice campaign start (20 calls) | < 3 seconds |
| Medical report OCR | < 5 seconds |
| Frontend page load | < 2 seconds |
| API response (95th percentile) | < 1 second |

---

## Team Execution Plan

### Team Structure
- **Team Size**: 2 members
- **Time Constraint**: 10 hours
- **Tools**: AI-assisted development (Claude Code, Cursor, Copilot)

### Task Split

#### Person A (Frontend Lead)

**Responsibilities**:
- Next.js frontend architecture
- UI/UX design implementation
- API integration (React Query)
- Vercel deployment
- Demo rehearsal

**Hour-by-Hour Plan**:

| Hour | Task | Deliverable |
|------|------|-------------|
| 1-2 | Setup | Next.js project, Tailwind, shadcn/ui, Vercel deploy, Cognito auth |
| 3-5 | Patient + Donor Portals | Patient registration, medical report upload, status tracker, donor login, profile, history, badges |
| 6-8 | Coordinator Dashboard | Active requests table, donor matching view (top 20 with scores, map), WhatsApp campaign progress, voice call progress, blood bank inventory heatmap, document verification queue |
| 9-10 | Polish + Demo | Loading states, error handling, mock data (100 donors from Dataset.md), demo rehearsal |

#### Person B (Backend Lead)

**Responsibilities**:
- FastAPI backend architecture
- Database schema (DynamoDB)
- AI/ML services (OCR, matching, urgency)
- AWS integrations (Textract, Polly, Connect)
- Communication services (WhatsApp, voice calls)

**Hour-by-Hour Plan**:

| Hour | Task | Deliverable |
|------|------|-------------|
| 1-2 | Setup | FastAPI project, DynamoDB tables (donors, patients, requests, blood_banks), S3 bucket |
| 3-5 | Core Services | Document Verifier (Textract OCR + AI model), Urgency Calculator, Donor Matching Engine (readiness score), Inventory service |
| 6-8 | Communication Services | WhatsApp service (Twilio), voice call service (Exotel/Twilio), webhook handlers, notification system |
| 9-10 | Integration | Connect frontend to backend, load Dataset.md into DynamoDB (100 donors), test end-to-end flow, prepare failure case answers |

---

## Document Sharing Strategy

### Shared Documents

1. **Database Schema** (Both agree on Hour 1)
   - `donors` table schema (based on Dataset.md)
   - `patients` table schema
   - `requests` table schema
   - `blood_banks` table schema

2. **API Contract** (Both agree on Hour 1)
   - REST API endpoints specification
   - Request/response formats (JSON)
   - Error codes and messages

3. **Mock Data** (Person B provides by Hour 9)
   - 100 donors from Dataset.md (loaded into DynamoDB)
   - 10 patients (test cases)
   - 5 blood banks (mock inventory)

4. **Demo Script** (Both finalize by Hour 10)
   - 3-minute pitch
   - Step-by-step demo flow
   - Failure case answers

### Communication Protocol

- **Real-time**: Discord/Slack for quick questions
- **Code sharing**: GitHub repo with branch protection
- **Document sharing**: Google Drive for schema, API contract, demo script
- **Hourly check-in**: 5-minute standup every hour (what done, what next, blockers)

---

## Testing Strategy

### Unit Testing (Person B)

**Document Verifier**:
```python
def test_extract_hb_value():
    # Test OCR extraction with confidence threshold
    assert extract_hb("Hb: 6.8 g/dL") == {"value": 6.8, "confidence": 0.95}

def test_urgency_calculation():
    # Test urgency window calculation
    assert calculate_urgency(hb=6.8, ferritin=12, days_since=17) == 4
```

**Donor Matching Engine**:
```python
def test_readiness_score_eligible_donor():
    # Test score calculation for eligible donor
    donor = {"eligibility_status": "eligible", "calls_to_donations_ratio": 0.33}
    patient = {"bridge_blood_group": "O Positive"}
    assert calculate_donor_readiness_score(donor, patient) > 80

def test_blood_group_compatibility():
    # Test O- can donate to anyone
    assert is_compatible("O Negative", "A Positive") == True
```

### Integration Testing (Both)

**End-to-End Flow**:
1. Patient registers → uploads medical report
2. Document verifier extracts Hb=6.8, Ferritin=12, last_transfusion=2025-08-02
3. Urgency calculator returns 4-day window
4. Coordinator clicks "Find Donors"
5. Donor matching returns top 20 with scores
6. Coordinator starts WhatsApp campaign → 50 messages sent → 8 reply yes
7. AI calls 8 donors → 5 confirm
8. Donation day → reminder sent → donor donates → feedback collected

**Test Cases**:
- Happy path (all donors confirm, donation successful)
- Failure path (all donors decline, expand to Tier 2)
- Edge case (OCR misreads Hb, flag for human review)
- Race condition (multiple patients reserve same blood bank stock)

### Demo Testing (Both, Hour 10)

**Pre-Demo Checklist**:
- [ ] Patient registration works (form submit → DynamoDB write)
- [ ] Medical report upload works (S3 upload → Textract OCR → field extraction)
- [ ] Donor matching works (returns top 20 with correct scores)
- [ ] WhatsApp campaign works (messages sent → replies tracked)
- [ ] Coordinator dashboard updates in real-time
- [ ] Blood bank inventory displays correctly
- [ ] Document verification queue shows pending approvals

**Fallback Plan**:
- If live demo fails → show pre-recorded video
- If API fails → use mock data (frontend hardcoded responses)
- If AWS service fails → explain architecture, show UI mockups

---

## 10-Hour Execution Timeline

### Hour 0: Kickoff (Both)
- Agree on database schema
- Agree on API contract
- Create GitHub repo
- Person A: `npx create-next-app@latest`
- Person B: `fastapi new praan-backend`

### Hour 1-2: Foundation
**Person A**:
- Next.js setup (App Router, Tailwind, shadcn/ui)
- Vercel deploy (auto-deploy on push)
- Cognito auth integration

**Person B**:
- FastAPI project structure
- DynamoDB table creation (boto3 scripts)
- S3 bucket setup
- Basic auth (Cognito)

### Hour 3-5: Core Features
**Person A**:
- Patient registration form (name, age, blood group, hospital, location)
- Medical report upload UI (PDF/image)
- Status tracker (urgency countdown display)
- Donor login + profile page
- Donor history + badges

**Person B**:
- Document Verifier (Textract OCR + field extraction + confidence scoring)
- Urgency Calculator (Hb, Ferritin, days_since_last_transfusion)
- Donor Matching Engine (readiness score using Dataset.md parameters)
- Inventory service (mock eRaktKosh data)

### Hour 5-7: Communication
**Person A**:
- Coordinator dashboard (requests table, donor matching view)
- WhatsApp campaign progress (sent/replied/confirmed)
- Voice call progress (called/responded/confirmed)
- Blood bank inventory heatmap

**Person B**:
- WhatsApp service (Twilio integration)
- Voice call service (Exotel/Twilio, pre-recorded message)
- Webhook handlers (WhatsApp replies, call responses)
- Notification system (reminders)

### Hour 7-9: Integration
**Person A**:
- Dashboard progress views (WhatsApp/call status)
- Document verification queue (pending approvals)
- Loading states, error handling

**Person B**:
- Connect frontend to backend (API endpoints)
- Load Dataset.md into DynamoDB (100 donors)
- Test end-to-end flow
- Fix bugs

### Hour 9-10: Demo Prep
**Both**:
- Load test data (50 patients, 500 donors, 10 blood banks)
- Rehearse 3-minute demo
- Prepare failure case answers
- Record fallback video (if live demo fails)

---

## Demo Strategy

### What to BUILD (show working):
1. **Document Verifier** — Textract OCR extracts Hb, Ferritin, dates from medical report
2. **Donor Matching Engine** — Readiness score algorithm ranks top 20 donors
3. **Urgency Calculator** — Calculates 4-day window from OCR data
4. **Coordinator Dashboard** — Active requests, donor matching, WhatsApp/call progress
5. **WhatsApp Campaign** — Send messages, track replies (Twilio integration)

### What to FAKE (explain architecture):
1. **Bedrock Chatbot** — Show UI, explain "we use Bedrock Claude for conversational AI"
2. **Voice AI (Lex)** — Show pre-recorded message, explain "we use Lex for NLU"
3. **Predictive ML (SageMaker)** — Explain "we train on Blood Warriors historical data"
4. **Full eRaktKosh Integration** — Explain "we have API access via MOU"
5. **AI Verification Model** — Show rule-based logic, explain "we train classifier on synthetic data"

### 3-Minute Demo Script

**Minute 1**: Patient Journey
- Patient registers → uploads medical report
- Document verifier extracts Hb=6.8, Ferritin=12, last_transfusion=2025-08-02
- Urgency calculator shows "4-day window (critical)"

**Minute 2**: Coordinator Actions
- Coordinator sees request on dashboard
- Clicks "Find Donors" → system shows top 20 with scores
- Starts WhatsApp campaign → 50 messages sent → 8 reply yes

**Minute 3**: Donor Conversion
- AI calls 8 donors → 5 confirm → show live progress
- Donation day → reminder sent → donor donates → feedback collected
- Donor retention → show badge "5 Lives Saved"

**Closing**: "We built PRAAN AI in 10 hours. Document verification, donor matching, WhatsApp campaigns, voice calls. Real data from Blood Warriors. Ready to deploy."

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| AWS service fails during demo | Use mock mode (APP_MODE=mock), hardcoded responses |
| Textract OCR low accuracy | Show confidence threshold, flag for human review |
| Twilio/Exotel API quota exceeded | Pre-record WhatsApp messages, show UI mockups |
| DynamoDB rate limits | Use local DynamoDB for demo, not AWS |
| Frontend crashes | Record fallback video, show screenshots |

### Time Risks

| Risk | Mitigation |
|------|------------|
| Backend takes longer than 5 hours | Skip voice call service, use WhatsApp only |
| Frontend takes longer than 5 hours | Simplify UI, use shadcn/ui default components |
| Integration fails | Demo backend and frontend separately |
| Demo rehearsal fails | Show pre-recorded video |

### Scope Risks

| Risk | Mitigation |
|------|------------|
| Too many features to build | Focus on core: patient → matching → WhatsApp → calls |
| Jury asks about missing features | Explain architecture, show it's planned for production |
| Dataset.md format incompatible | Pre-process into JSON, load into DynamoDB before demo |

---

## Post-Hackathon Roadmap

### Phase 1: MVP (1 month)
- Full eRaktKosh API integration (MOU with MoHFW)
- Production-grade document verifier (train AI model on 1000 synthetic reports)
- Blood bank partnership (5-10 hospitals in Hyderabad)
- Donor consent management (DISHA compliance)

### Phase 2: Scale (3 months)
- Expansion to 5 cities (Hyderabad, Chennai, Bangalore, Mumbai, Delhi)
- Mobile app (React Native)
- Predictive ML model (SageMaker) for demand forecasting
- Replacement donation workflow

### Phase 3: National (12 months)
- 100+ blood bank partnerships
- 50,000+ active donors
- Government grant funding
- Component blood tracking (PRBC, platelets, FFP)
- Multilingual support (12 languages)

---

## Success Metrics

### Hackathon Demo Success
- [ ] Patient registration works end-to-end
- [ ] Document verifier extracts fields with >80% confidence
- [ ] Donor matching returns top 20 with correct scores
- [ ] WhatsApp campaign sends 50 messages, tracks 8 replies
- [ ] Coordinator dashboard updates in real-time
- [ ] Demo completes in <3 minutes
- [ ] Jury asks questions about failure cases (shows interest)

### Production Success (6 months)
- Reduce coordinator time from 2 hours → 5 minutes per patient
- Increase donor conversion rate from 10% → 30%
- Reduce patient wait time from 7 days → 2 days
- Scale from 5,596 donors → 50,000 donors
- Partner with 100+ blood banks across India
