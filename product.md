# PRAAN AI — Product Specification

> AI-Powered Blood Coordination for Thalassemia Fighters
> PRAAN AI × Blood Warriors Collaboration

---

## Product Identity

**Name**: PRAAN AI (Predictive Response & Automated Assistance Network)
**Partner**: Blood Warriors — India's leading Thalassemia blood coordination nonprofit
**Collaboration**: PRAAN AI × Blood Warriors
**Tagline**: "Every Drop Counts. Every Second Matters."

---

## Vision

A country where no Thalassemia patient waits for blood because the system already found it for them.

## Mission

Replace manual one-by-one donor calling with an intelligent AI brain that checks blood banks first, calculates exactly how many days a patient can wait, and calls 20 donors simultaneously in their language — turning a 2-hour coordinator task into a 5-minute automated workflow.

---

## The Problem We Solve

### Current State (Blood Warriors Today)
- Coordinator receives patient request → manually calls blood banks to check stock
- If no stock → manually calls donors one by one (20 calls = 2 hours)
- No system reads patient medical reports to understand urgency
- No tracking of which donors actually convert from calls to donations
- Failure patterns not learned (same areas fail, same blood groups fail)
- All in English — donors in rural Telangana don't understand

### Future State (With PRAAN AI)
- System checks blood bank inventory automatically → reserves if available
- If insufficient → ranks top 20 donors by readiness score
- AI calls all 20 simultaneously → speaks in donor's language
- System reads patient's medical report → calculates urgency countdown
- Every failure teaches the system → next time it's smarter
- Multilingual: Tamil, Hindi, Gujarati, Bengali, Marathi, Telugu

---

## 3 Differentiators (What Makes Us Different)

### 1. Blood Bank Inventory Automation
**What other teams do**: Start by searching for donors.
**What we do**: Check blood banks first. Donors are the last resort.

```
Patient needs O+, 2 units
→ System queries 30+ blood banks in the district
→ Apollo Blood Bank has 5 units, expires Oct 15
→ Auto-reserve 2 units via API
→ Only if blood banks can't fulfill → activate donor search
→ "Blood bank first, donor last"
```

**Why it matters**: Blood Warriors currently has one person manually calling blood banks. We automate the entire search, reserve, and expiry tracking process.

### 2. Transfusion Urgency Window
**What other teams do**: Assume all patients are equally urgent.
**What we do**: Calculate exactly how many days each patient can wait.

```
Patient Kavya uploads medical report:
→ Textract reads: Hb 6.8 g/dL, Ferritin 12 ng/mL
→ System knows: last transfusion Aug 2, cycle 21 days
→ Calculates: urgency window = 4 days
→ System starts donor search TODAY, not next week

Patient Rahul's report:
→ Hb 9.2 g/dL, Ferritin 45 ng/mL
→ Last transfusion Aug 10, cycle 28 days
→ Urgency window = 12 days
→ System schedules search for next week
```

**Why it matters**: Not every patient needs blood tomorrow. Some have 3 days, some have 21. The system prioritizes based on real medical data, not guesses.

### 3. AI Voice Call Assistant (20 Parallel Calls)
**What other teams do**: Send SMS/push notifications, wait for responses.
**What we do**: Call all 20 donors simultaneously, speak in their language, collect responses in real-time.

```
System triggers campaign:
→ Amazon Connect calls 20 donors at once
→ Polly speaks: "Namaste, Blood Warriors here. A patient with O+ 
   blood needs your help this week. Can you donate? Press 1 for yes."
→ Lex understands voice responses (not just button presses)
→ Dashboard shows live status: 3 confirmed, 5 declined, 12 still calling
→ First 3 confirmed → remaining 17 get "Thank you, donors found"
```

**Why it matters**: A coordinator calling 20 people one-by-one takes 2 hours. Our system does it in 5 minutes, in 6 languages, with zero manual effort.

---

## User Personas

### 1. Patient / Patient's Parent
**Who**: Parent of a Thalassemia child (age 5-15)
**Need**: Blood every 2-4 weeks for their child
**Pain point**: Uncertainty — will blood be available on time?
**Interaction**: Upload medical report → see urgency countdown → track donor search progress

### 2. Donor
**Who**: Regular blood donor, age 20-45, registered with Blood Warriors
**Need**: Clear information about when and where to donate
**Pain point**: Gets called too often, sometimes for wrong blood group
**Interaction**: Receives AI voice call in their language → says yes/no → gets confirmation + location

### 3. Coordinator (Blood Warriors Staff)
**Who**: Blood Warriors team member managing multiple patient requests
**Need**: See all active requests, their urgency, and donor search status
**Pain point**: Overwhelmed by manual calling, tracking in spreadsheets
**Interaction**: Command center dashboard → sees workflow timeline → intervenes only when AI gets stuck

### 4. Blood Bank Admin
**Who**: Staff at a hospital blood bank
**Need**: Manage inventory, track expiry dates, fulfill reservation requests
**Pain point**: No automated system — uses phone calls and paper records
**Interaction**: Inventory dashboard → sees reservation requests → confirms/rejects → gets expiry alerts

---

## Feature List by Module

### Module 1: Patient Onboarding
- Patient registration form (name, age, blood group, location, contact)
- Medical report upload (PDF/image of blood test)
- OCR extraction: Hb, MCV, MCH, Ferritin values
- Urgency window calculation with countdown timer
- Transfusion history tracking (last date, cycle length, expected next date)
- Consent management (DISHA compliance)

### Module 2: Blood Bank Inventory
- Real-time inventory by blood group across all partner blood banks
- Search by blood group + district
- Auto-reserve units when patient request comes in
- Expiry tracking with alerts (7-day warning)
- Stock analytics (which groups are running low)
- Reserve/release workflow

### Module 3: Donor Matching & Ranking
- Donor Readiness Score from 5 signals:
  1. Eligibility (120-day gap from last donation)
  2. Reliability (calls_to_donations_ratio from dataset)
  3. Availability patterns (time of day, day of week)
  4. Willingness (recent response history)
  5. Proximity (KNN geospatial from latitude/longitude)
- Tier system: Tier 1 (top 5) → Tier 2 (next 10) → Tier 3 (remaining)
- Blood group compatibility matching

### Module 4: AI Voice Call Campaign
- Parallel outbound calls (up to 20 simultaneously)
- Multilingual voice scripts (6 languages via Polly)
- Voice response understanding (Lex NLU)
- Real-time response tracking (confirmed/declined/no-answer)
- Auto-cancel remaining calls when target met
- Retry logic for no-answer (2 hours later)
- Fallback to SMS if call fails

### Module 5: Coordinator Command Center
- Unified workflow timeline (patient → blood bank → donors → confirmed)
- Active patients with urgency countdowns
- Donor readiness leaderboard
- Failure insights ("Last 3 O+ requests in Hyderabad needed Tier 2")
- Real-time activity feed
- Self-improving system metrics

### Module 6: Conversational AI Layer
- Bedrock-powered chatbot for patient/donor queries
- Memory across sessions (DynamoDB session store)
- Multilingual support (6 languages)
- WhatsApp integration via API
- Emotional, human-like responses (not robotic)

---

## AWS Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                     │
│         Amplify / S3 + CloudFront Deployment              │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                 API GATEWAY + Cognito Auth                │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│              PYTHON FASTAPI (Lambda / App Runner)         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Predict  │ │  Match   │ │ Automate │ │ Sustain  │   │
│  │ Engine   │ │ Engine   │ │ Engine   │ │ Engine   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Blood Bank Inventory Engine              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                    AWS SERVICES                           │
│  ┌────────┐ ┌──────────┐ ┌──────┐ ┌────────┐           │
│  │DynamoDB│ │ SageMaker│ │Bedrock│ │ Textract│           │
│  │  Data  │ │   ML     │ │  AI  │ │  OCR   │           │
│  └────────┘ └──────────┘ └──────┘ └────────┘           │
│  ┌──────────┐ ┌─────────┐ ┌─────┐ ┌─────┐             │
│  │ Connect  │ │  Polly  │ │ Lex │ │ SNS │              │
│  │  Voice   │ │  TTS    │ │ NLU │ │ SMS │              │
│  └──────────┘ └─────────┘ └─────┘ └─────┘             │
│  ┌─────┐ ┌────────────┐ ┌──────────┐                   │
│  │ SQS │ │ EventBridge│ │CloudWatch│                   │
│  │Queue│ │   Events   │ │  Logs    │                   │
│  └─────┘ └────────────┘ └──────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## Collaboration Value

| What Blood Warriors Brings | What PRAAN AI Brings |
|---|---|
| 5,596 registered donors | AI that ranks them by readiness |
| 4,366 blood collections | Automated inventory management |
| 134 community sessions | Predictive outreach that learns |
| Manual coordination | 20 parallel voice calls |
| WhatsApp-based requests | Multilingual AI conversations |
| Thalassemia expertise | Urgency window calculation |

**Together**: Blood Warriors provides the human network and domain expertise. PRAAN AI provides the intelligent automation that lets them scale from 5,596 donors to 50,000 without adding a single coordinator.

---

## Document Verification System (OCR + AI)

### Verification Pipeline

```
┌─────────────────────────────────────────────────────────┐
│              DOCUMENT VERIFICATION PIPELINE              │
└─────────────────────────────────────────────────────────┘

Patient uploads medical report (PDF/image)
         ↓
┌─────────────────────────────────┐
│  1. Textract OCR Extraction     │
│  - Extract text from PDF/image  │
│  - Confidence score per field   │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│  2. Field Extraction (RegEx)    │
│  - Hb: 6.8 g/dL                 │
│  - Ferritin: 12 ng/mL           │
│  - Last Transfusion: 2025-08-02 │
│  - Hospital Name: Apollo        │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│  3. AI Verification Model       │
│  - Document type classification │
│  - Anomaly detection            │
│  - Cross-field validation       │
└──────────┬──────────────────────┘
           ↓
┌─────────────────────────────────┐
│  4. Human Review Queue          │
│  - Flag if confidence < 80%     │
│  - Blood Warriors team approves │
└─────────────────────────────────┘
```

### Verification Logic

**Extracted Fields**:
- Hemoglobin (Hb): critical for urgency calculation
- Ferritin: indicates iron stores
- Last Transfusion Date: determines cycle position
- Hospital Name: verified against approved list

**Cross-Validation Rules**:
- Hb < 5.0 g/dL → flag as critically low, verify with hospital
- Last transfusion < 14 days ago → reject (too recent)
- Hospital not in verified list → flag for manual review
- OCR confidence < 80% → flag for human review

**Urgency Calculation**:
```python
def calculate_urgency(hb, ferritin, days_since_last_transfusion, cycle_length=21):
    remaining_days = cycle_length - days_since_last_transfusion
    
    if hb < 7.0:
        return min(remaining_days, 3)  # Critical: max 3 days
    elif hb < 9.0:
        return min(remaining_days, 7)  # Urgent: max 7 days
    else:
        return remaining_days  # Normal: use full cycle
```

**Document Authenticity Checks**:
- Verify hospital name against approved list
- Check for tampering (metadata analysis)
- Validate date formats and ranges
- Cross-reference with patient history

---

## Donor Matching Algorithm

### Donor Readiness Score (0-100)

Based on Blood Warriors dataset parameters:

| Parameter | Weight | Logic |
|-----------|--------|-------|
| **eligibility_status** | 30% | Must be "eligible" (next_eligible_date ≤ today) |
| **calls_to_donations_ratio** | 25% | Lower = better (0.17 excellent, 23.0 terrible) |
| **blood_group match** | 20% | Exact match = 20, compatible = 10, no match = 0 |
| **user_donation_active_status** | 15% | "Active" = 15, "Inactive" = 0 |
| **donations_till_date** | 10% | More donations = more reliable |

### Scoring Formula

```python
def calculate_donor_readiness_score(donor, patient):
    score = 0
    
    # 1. Eligibility Check (30 points)
    if donor['eligibility_status'] == 'eligible':
        if donor['next_eligible_date'] <= today:
            score += 30
    
    # 2. Reliability: calls_to_donations_ratio (25 points)
    ratio = donor.get('calls_to_donations_ratio', 999)
    if ratio <= 1.0:
        score += 25  # Excellent
    elif ratio <= 3.0:
        score += 20  # Good
    elif ratio <= 5.0:
        score += 15  # Average
    elif ratio <= 10.0:
        score += 10  # Below average
    
    # 3. Blood Group Match (20 points)
    if donor['blood_group'] == patient['bridge_blood_group']:
        score += 20  # Exact match
    elif is_compatible(donor['blood_group'], patient['bridge_blood_group']):
        score += 10  # Compatible
    
    # 4. Activity Status (15 points)
    if donor['user_donation_active_status'] == 'Active':
        score += 15
    
    # 5. Donation History (10 points)
    donations = donor.get('donations_till_date', 0)
    if donations >= 10:
        score += 10  # Veteran
    elif donations >= 5:
        score += 8   # Experienced
    elif donations >= 2:
        score += 5   # Some experience
    
    # 6. Bonus: Bridge Donor (already linked to patient)
    if donor['role'] == 'Bridge Donor':
        if donor['bridge_id'] == patient['bridge_id']:
            score += 10
    
    # 7. Proximity (geospatial)
    distance_km = haversine_distance(donor, patient)
    if distance_km <= 5:
        score += 10
    elif distance_km <= 10:
        score += 7
    elif distance_km <= 25:
        score += 4
    
    return min(score, 100)
```

### Blood Group Compatibility

| Patient Blood Group | Compatible Donors |
|---------------------|-------------------|
| A+ | A+, A-, O- |
| A- | A-, O- |
| B+ | B+, B-, O- |
| B- | B-, O- |
| AB+ | AB+, AB-, A-, B-, O- |
| AB- | AB-, A-, B-, O- |
| O+ | O+, O- |
| O- | O- (universal donor) |

### Matching Workflow

1. **Filter**: Exclude donors with `eligibility_status = 'not eligible'` or `next_eligible_date > today`
2. **Score**: Calculate readiness score (0-100) for each eligible donor
3. **Rank**: Sort by score descending
4. **Select**: Pick top 20 donors (Tier 1)
5. **Expand**: If <2 confirm, expand to top 50 (Tier 2), then top 100 (Tier 3)

---

## WhatsApp → Voice Call Funnel

### Communication Strategy

**Step 1: WhatsApp Campaign**
- Send to top 50 donors (Tier 1 + Tier 2)
- Template message (pre-approved by Blood Warriors):
  ```
  "Namaste [Donor Name], Blood Warriors here. A patient with [Blood Group] 
  blood needs your help. Can you donate this week? Reply YES or NO."
  ```
- Track: sent, delivered, read, replied

**Expected Conversion**:
- 50 messages sent → 30 open (60%) → 15 read (30%) → 8 reply (16%)
- 8 reply YES → proceed to voice calls

**Step 2: Voice Call Campaign**
- Call 8 donors who replied YES
- Pre-recorded message + button response:
  ```
  "Namaste, this is PRAAN AI calling for Blood Warriors. A patient needs 
  [Blood Group] blood. Press 1 to confirm donation, Press 2 to decline, 
  Press 0 to opt out of future calls."
  ```
- Track: called, picked up, responded, confirmed

**Expected Conversion**:
- 8 called → 6 pick up (75%) → 5 confirm (83% of pickup)
- 5 confirmed donors

**Step 3: Pre-Donation Reminders**
- T-7 days: "You're scheduled for [date]"
- T-3 days: Pre-donation instructions (eat well, sleep 8 hours)
- T-1 day: Final confirmation + hospital address + time slot
- T-0 (donation day): Morning reminder with map link

**Step 4: Post-Donation Feedback**
- T+1 day: Thank you + feedback request
- Collect: experience rating, suggestions, willingness to donate again

### Retry Logic

**No Response on WhatsApp**:
- Retry after 4 hours (send to another 50 donors)
- Max 2 retries per request

**No Answer on Voice Call**:
- Retry after 2 hours (max 3 attempts)
- Fallback to SMS if all attempts fail

**Donor Declines**:
- Respect decision, don't retry
- Log for future analysis (why declining?)

---

## Donor Retention Strategy

### 1. Gamification

**Badges**:
- "First Donor" — completed first donation
- "5 Lives Saved" — 5 successful donations
- "Rare Blood Hero" — donated rare blood group (O-, AB-)
- "Bridge Donor" — regular donor for specific patient

**Leaderboard**:
- Top donors in city (by donations count)
- Monthly/quarterly rankings
- Shareable on WhatsApp status

**Certificates**:
- "I saved X lives this year" (downloadable PDF)
- Annual donor appreciation certificate

### 2. Health Benefits

**Free Health Checkups**:
- After every 3 donations → free health checkup (partner with hospitals)
- Includes: CBC, lipid profile, blood sugar, BP

**Blood Test Reports**:
- After each donation → send donor's own blood test report
- Includes: Hb, cholesterol, blood sugar
- Donors love seeing their health metrics

**Health Tips**:
- Weekly WhatsApp messages (not spam — valuable content)
- Topics: nutrition, exercise, blood donation benefits
- Personalized based on donor's health data

### 3. Social Proof

**Impact Stories**:
- "Your donation helped [Patient Name]" (with patient consent)
- Video thank-you from patient family
- Shareable on social media

**Annual Events**:
- Donor appreciation ceremony (Blood Warriors already does this)
- Awards: "Donor of the Year", "Most Reliable Donor"
- Media coverage

### 4. Convenience

**Preferred Time Slots**:
- Remember donor's availability (9AM-6PM, weekends only)
- Don't call outside preferred hours

**Mobile Blood Collection**:
- Van at donor's office/college (partner with mobile blood banks)
- No need to travel to hospital

**VIP Treatment**:
- Skip queue at blood bank (repeat donors)
- Dedicated coordinator for top donors

### 5. Community

**Donor WhatsApp Groups**:
- City-wise groups (Hyderabad Donors, Chennai Donors)
- Share success stories, donation camps, health tips

**Referral Program**:
- Bring a friend → both get recognition
- "Refer 5 friends" badge

**Donor of the Month**:
- Spotlight on Blood Warriors website/social media
- Interview, photo, impact story

---

## Failure Cases & Backup Plans

### Failure 1: Hospital Verification Delays

**Scenario**: Patient urgent (2-day window), hospital takes 1 day to verify

**Backup**:
- Pre-approved hospital list (skip verification for trusted hospitals like Apollo, Fortis)
- Coordinator fast-tracks with phone call to hospital
- Show "verification in progress" on dashboard, don't block workflow

### Failure 2: All Donors Decline

**Scenario**: 50 WhatsApp sent, 0 say yes

**Backup**:
- Expand to Tier 2 donors (next 50 donors, lower scores)
- Expand search radius (5km → 10km → 25km)
- Try alternative blood groups (O- universal donor)
- Alert coordinator for manual intervention
- Suggest patient try other blood coordination NGOs (Red Cross, Rotary)

### Failure 3: Blood Bank Stock Mismatch

**Scenario**: System shows 5 units, reality is 0 (stale data)

**Backup**:
- Show "last updated: X hours ago" timestamp
- Flag as "unverified" if >6 hours old
- Coordinator calls blood bank to confirm BEFORE sending patient
- If mismatch → log as data quality issue → alert other coordinators
- Prioritize recently updated blood banks in search results

### Failure 4: Donor No-Show on Donation Day

**Scenario**: Donor said yes, didn't show up

**Backup**:
- Over-recruit by 50% (need 3 donors, confirm 5)
- Have 2 backup donors ready (call same day)
- Track no-show rate per donor → penalize readiness score
- Send T-0 morning reminder with map link

### Failure 5: Patient Condition Worsens

**Scenario**: Urgency window was 7 days, now 2 days

**Backup**:
- Escalate to "emergency mode" → coordinator takes over manually
- Expand donor search to all 5,596 donors
- Contact emergency blood banks (24/7 operations)
- Alert hospital to prepare alternative treatments

### Failure 6: AI Call Fails (Network/Technical)

**Scenario**: Call drops, audio unclear, donor doesn't understand

**Backup**:
- Fallback to SMS/WhatsApp text
- Coordinator manual call
- Log failure for debugging (network issue vs script issue)
- Retry after 2 hours (max 3 attempts)

### Failure 7: Donor Complaint (Harassment/Spam)

**Scenario**: Donor angry about too many calls/messages

**Backup**:
- Immediate opt-out ("Press 0 to never be called again")
- Route to human coordinator for apology
- Review call frequency limits (max 2 calls per month per donor)
- Log complaint for analysis

### Failure 8: OCR Misreads Medical Report

**Scenario**: Hb 6.8 read as 68 (decimal point missed)

**Backup**:
- Confidence threshold: if OCR confidence < 80%, flag for human review
- Cross-validation: Hb > 20 g/dL is impossible → flag as error
- Don't auto-calculate urgency from low-confidence data
- Show "verification pending" on dashboard

### Failure 9: Multiple Patients Reserve Same Blood Bank Stock

**Scenario**: Race condition — 2 patients reserve same 2 units

**Backup**:
- DynamoDB conditional writes (atomic reservation)
- Only first reservation wins
- Second patient gets "stock unavailable" → try next blood bank
- Alert coordinator to resolve conflict

### Failure 10: WhatsApp/Call Timing Issues

**Scenario**: Call at 3 AM / wrong timezone / donor sleeping

**Backup**:
- Respect donor's preferred time window (default 9AM-8PM)
- Track timezone from phone number
- Donor can set preferred hours in profile
- Log complaints about timing → adjust algorithm

---

## Cost Model

### Per Patient Request

| Service | Cost | Notes |
|---------|------|-------|
| WhatsApp messages | ₹25 | 50 messages × ₹0.50 |
| Voice calls | ₹20 | 10 calls × ₹2/min × 1 min |
| AWS Textract (OCR) | ₹10 | 1 medical report |
| AWS DynamoDB | ₹5 | Read/write operations |
| AWS Lambda | ₹5 | Compute time |
| AWS S3 | ₹2 | Medical report storage |
| Coordinator time | ₹30 | 5 minutes × ₹6/hour |
| **Total** | **₹97** | **Per patient request** |

### Monthly Costs (100 patients/month)

| Category | Cost |
|----------|------|
| Communication (WhatsApp + calls) | ₹4,500 |
| AWS services | ₹2,200 |
| Coordinator time | ₹3,000 |
| **Total** | **₹9,700/month** |

### Sustainability

**Funding Sources**:
- Government grants (National Health Mission)
- CSR funds (corporate social responsibility)
- Blood Warriors existing budget
- Patient contribution (optional, ₹100-200 per request)

**Cost Optimization**:
- Bulk WhatsApp Business API pricing (₹0.30/message at scale)
- AWS nonprofit credits (up to $5,000/year)
- Volunteer coordinators (reduce labor cost)
- Optimize donor matching (reduce failed calls)

---

## Regulatory Compliance

### DISHA (Digital Information Security in Healthcare Act)

**Requirements**:
- Patient consent required before data processing
- Medical data encrypted at rest (DynamoDB encryption) and in transit (HTTPS)
- Consent withdrawal API: patient can revoke data access
- Data retention policy: medical reports auto-deleted after 90 days
- Audit trail: log all data access

**Implementation**:
- Consent checkbox on patient registration form
- Encryption keys managed by AWS KMS
- Consent withdrawal endpoint: `DELETE /api/patient/{id}/consent`
- Scheduled Lambda function deletes reports >90 days old
- DynamoDB streams log all read/write operations

### DPDPA 2023 (Digital Personal Data Protection Act)

**Requirements**:
- Donor PII (phone, location) protected
- Data minimization: collect only what's needed
- Right to erasure: donor can request data deletion
- Data localization: store data in India (ap-south-1)

**Implementation**:
- Encrypt donor phone numbers in DynamoDB
- Collect only: name, phone, blood group, location, donation history
- Data deletion endpoint: `DELETE /api/donor/{id}`
- All AWS services in Mumbai region (ap-south-1)

### CDSCO (Central Drugs Standard Control Organization)

**Requirements**:
- Blood banks need CDSCO permission to share inventory data
- MOU required between PRAAN AI and blood banks
- Data sharing agreement with terms and conditions

**Implementation**:
- Partner with Blood Warriors (they have existing MOUs)
- Draft data sharing agreement template
- Legal review by Blood Warriors legal team
- Start with 5-10 partner hospitals (scale gradually)

### NBTC (National Blood Transfusion Council)

**Requirements**:
- Follow NBTC guidelines for blood donation
- 120-day gap between whole blood donations
- Donor eligibility criteria (age, weight, health)

**Implementation**:
- Enforce 120-day gap in readiness score algorithm
- Check `next_eligible_date` before matching
- Flag donors who don't meet NBTC criteria

---

## eRaktKosh Integration Strategy

### Current Reality

**eRaktKosh Limitations**:
- No public API for third-party integration
- Blood banks manually update stock (data often 2-6 hours stale)
- No reservation API — can't auto-reserve units
- Many small blood banks don't use eRaktKosh

### Integration Approach

**Phase 1: Manual Integration (Hackathon Demo)**
- Blood bank portal: staff manually updates inventory
- System shows "last updated: X hours ago" timestamp
- Coordinator calls blood bank to confirm before sending patient

**Phase 2: Partnership Integration (Production)**
- MOU with MoHFW (Ministry of Health and Family Welfare)
- Read-only API access to eRaktKosh data
- Automated data sync (pull every 15 minutes)
- Still require manual confirmation for reservations

**Phase 3: Direct Integration (Scale)**
- Partner with 100+ blood banks directly
- API integration with hospital EMR systems
- Real-time inventory updates
- Automated reservation workflow

### Data Quality Validation

**Freshness Checks**:
- Flag as "unverified" if last update >6 hours old
- Prioritize recently updated blood banks in search
- Show confidence score: "Updated 2 hours ago" vs "Updated yesterday"

**Accuracy Checks**:
- Cross-reference with coordinator manual calls
- Log mismatches (system says 5 units, reality is 0)
- Penalize blood banks with poor data quality

**Completeness Checks**:
- Flag blood banks that don't update component blood (PRBC vs whole blood)
- Alert coordinator if critical blood groups missing

---

## Component Blood Tracking

### Blood Components

**Thalassemia Patients Need**:
- **PRBC (Packed Red Blood Cells)** — most common for Thalassemia
- Not whole blood (separated into components)

**Other Components**:
- **Platelets** — for dengue, cancer patients
- **FFP (Fresh Frozen Plasma)** — for trauma, surgery
- **Cryoprecipitate** — for hemophilia

### Tracking Requirements

**Blood Bank Inventory**:
- Track by component: `inventory: {PRBC: {A+: 5, O+: 3}, Platelets: {B+: 2}}`
- Track expiry dates separately for each component
- Component-specific reservation workflow

**Patient Request**:
- Specify component: `component: "PRBC"`
- Match against blood bank component inventory
- Donor search matches component availability

### Dataset Enhancement

**Current Dataset.md**: Tracks only blood group (A+, O+, etc.)

**Enhanced Schema**:
```json
{
  "blood_group": "O Positive",
  "component": "PRBC",  // NEW FIELD
  "units_available": 5,
  "expiry_date": "2025-10-15"
}
```

---

## Replacement Donation Workflow

### Indian Law Requirement

**Replacement Donation System**:
- Patient's family must provide 1-2 replacement donors for every unit taken
- Blood bank won't release blood without replacement donors
- This is law in most Indian states

### Parallel Workflow

**Current Workflow**:
1. Find blood for patient (from blood bank or donors)
2. Patient receives transfusion

**Enhanced Workflow**:
1. Find blood for patient (from blood bank or donors)
2. **Parallel**: Find replacement donors (patient's family provides)
3. Blood bank releases blood only after replacement donors confirmed
4. Patient receives transfusion
5. Replacement donors donate (within 7 days)

### Implementation

**Replacement Donor Search**:
- Patient's family provides 2-3 potential replacement donors
- System verifies eligibility (120-day gap, health criteria)
- Schedule donation appointments
- Track replacement fulfillment

**Dashboard Updates**:
- Show "Blood found: ✓" and "Replacement donors: ✗"
- Alert if replacement donors not found within 3 days
- Coordinator intervenes to help family find replacement donors

**Failure Case**:
- If replacement donors not found → blood bank may refuse
- Coordinator escalates to hospital social worker
- Suggest alternative: voluntary donation camps

---

## Team Execution Plan

### Team Structure
- **Team Size**: 2 members
- **Time Constraint**: 10 hours
- **Tools**: AI-assisted development (Claude Code, Cursor, Copilot)

### Task Split

#### Person A (Frontend Lead)
- Next.js frontend architecture
- UI/UX design implementation
- API integration (React Query)
- Vercel deployment
- Demo rehearsal

#### Person B (Backend Lead)
- FastAPI backend architecture
- Database schema (DynamoDB)
- AI/ML services (OCR, matching, urgency)
- AWS integrations (Textract, Polly, Connect)
- Communication services (WhatsApp, voice calls)

### Document Sharing Strategy

**Shared Documents** (Both agree on Hour 1):
1. Database schema (donors, patients, requests, blood_banks)
2. API contract (REST endpoints, request/response formats)
3. Mock data (100 donors from Dataset.md, loaded into DynamoDB by Hour 9)
4. Demo script (3-minute pitch, failure case answers)

**Communication Protocol**:
- Real-time: Discord/Slack for quick questions
- Code sharing: GitHub repo with branch protection
- Document sharing: Google Drive for schema, API contract, demo script
- Hourly check-in: 5-minute standup every hour

### Testing Strategy

**Unit Testing** (Person B):
- Document verifier: OCR extraction, confidence scoring
- Donor matching: readiness score calculation, blood group compatibility
- Urgency calculator: Hb/Ferritin-based calculations

**Integration Testing** (Both):
- End-to-end flow: patient → matching → WhatsApp → calls → donation
- Happy path, failure path, edge cases

**Demo Testing** (Both, Hour 10):
- Pre-demo checklist: registration, upload, matching, WhatsApp, dashboard
- Fallback plan: pre-recorded video, mock data, UI mockups

### 10-Hour Execution Timeline

**Hour 0**: Kickoff (agree on schema, API contract, create GitHub repo)
**Hour 1-2**: Foundation (Next.js + FastAPI setup, DynamoDB tables)
**Hour 3-5**: Core features (Document verifier, donor matching, urgency calculator)
**Hour 5-7**: Communication (WhatsApp service, voice calls, coordinator dashboard)
**Hour 7-9**: Integration (connect frontend to backend, load Dataset.md, test flow)
**Hour 9-10**: Demo prep (test data, rehearse demo, prepare failure answers)

### Demo Strategy

**What to BUILD** (show working):
1. Document Verifier — Textract OCR extracts Hb, Ferritin, dates
2. Donor Matching Engine — Readiness score algorithm ranks top 20 donors
3. Urgency Calculator — Calculates 4-day window from OCR data
4. Coordinator Dashboard — Active requests, donor matching, WhatsApp/call progress
5. WhatsApp Campaign — Send messages, track replies (Twilio integration)

**What to FAKE** (explain architecture):
1. Bedrock Chatbot — Show UI, explain "we use Bedrock Claude"
2. Voice AI (Lex) — Show pre-recorded message, explain NLU
3. Predictive ML (SageMaker) — Explain "we train on historical data"
4. Full eRaktKosh Integration — Explain "we have API access via MOU"
5. AI Verification Model — Show rule-based logic, explain classifier training

### Risk Mitigation

**Technical Risks**:
- AWS service fails → use mock mode (APP_MODE=mock)
- Textract low accuracy → show confidence threshold, flag for human review
- Twilio quota exceeded → pre-record messages, show UI mockups

**Time Risks**:
- Backend takes longer → skip voice calls, use WhatsApp only
- Frontend takes longer → simplify UI, use default components
- Integration fails → demo backend and frontend separately

**Scope Risks**:
- Too many features → focus on core: patient → matching → WhatsApp → calls
- Jury asks about missing features → explain architecture, show planned for production
- Dataset.md incompatible → pre-process into JSON, load before demo

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
