# PRAAN AI — UI Card Specifications

> Design System × Component Library × Page Layouts
> Blood Warriors Brand Colors × Dark Theme × Card-Based UI

---

## Design System

### Color Palette
```css
/* Primary */
--red:        #FD6666;   /* Blood/action color */
--orange:     #FCAA49;   /* Warning/urgency */
--blue:       #41A7F1;   /* Info/calling */
--teal:       #64FFE3;   /* Success/confirmed */
--pink:       #FF5678;   /* Highlight/important */
--purple:     #AE41F1;   /* AI/intelligence */
--green:      #29D64F;   /* Positive/available */

/* Backgrounds (Dark Theme) */
--bg-primary:   #0F1117;
--bg-card:      #1A1D27;
--bg-card-hover:#242836;
--bg-surface:   #141720;

/* Text */
--text-primary:   #FFFFFF;
--text-secondary: #A0A3B1;
--text-muted:     #6B6E7B;

/* Borders */
--border:       #2A2D3A;
--border-focus: #41A7F1;
```

### Typography
- **Headings**: Inter, 700 weight
- **Body**: Inter, 400 weight
- **Mono**: JetBrains Mono (for data values, countdown timers)
- **H1**: 2.5rem, **H2**: 2rem, **H3**: 1.5rem, **Body**: 1rem, **Small**: 0.875rem

### Spacing
- Base unit: 4px
- Card padding: 24px
- Section gap: 32px
- Grid gap: 16px
- Component gap: 8px

### Border Radius
- Cards: 16px
- Buttons: 12px
- Inputs: 10px
- Badges: 8px
- Avatars: 50% (full round)

### Shadows
```css
--shadow-card: 0 4px 24px rgba(0,0,0,0.3);
--shadow-hover: 0 8px 32px rgba(0,0,0,0.4);
--shadow-glow-red: 0 0 20px rgba(253,102,102,0.3);
--shadow-glow-teal: 0 0 20px rgba(100,255,227,0.3);
```

---

## Component Inventory

### Layout Components

#### Navbar
```
┌──────────────────────────────────────────────────────────┐
│ [PRAAN AI] × [Blood Warriors]    Home  Demo  About  Login│
└──────────────────────────────────────────────────────────┘
Height: 64px, Background: bg-primary, Border-bottom: border
Logo: "PRAAN AI" text with heart icon (red) + "×" + Blood Warriors text
Nav links: text-secondary, hover: text-primary
Active link: underline with --red
```

#### Footer
```
┌──────────────────────────────────────────────────────────┐
│ PRAAN AI × Blood Warriors                                │
│ AI for Good 2.0 Hackathon | Built with AWS              │
│ Links: Problem Statement | Dataset | Architecture        │
└──────────────────────────────────────────────────────────┘
Background: bg-surface, Padding: 32px, Text: text-muted
```

---

### Reusable UI Components

#### Card
```
┌────────────────────────────┐
│                            │
│     Card Content Here      │
│                            │
└────────────────────────────┘
Background: bg-card
Border: 1px solid border
Border-radius: 16px
Padding: 24px
Shadow: shadow-card
Hover: bg-card-hover + shadow-hover
Transition: all 0.2s ease
```

#### StatCard
```
┌──────────────────────┐
│  🩸 5,596            │
│  Registered Donors    │
│  ↑ 12% this month    │
└──────────────────────┘
Top: Icon (40px circle, colored background)
Middle: Value (2rem, 700 weight, text-primary)
Bottom: Label (0.875rem, text-secondary)
Optional: Trend badge (green/red)
```

#### Button
```
Variants:
- Primary: bg --red, text white, hover darken 10%
- Secondary: bg transparent, border --red, text --red
- Ghost: bg transparent, text text-secondary
- Success: bg --teal, text black
- Danger: bg --pink, text white

Sizes:
- Small: padding 8px 16px, font 0.875rem
- Medium: padding 12px 24px, font 1rem
- Large: padding 16px 32px, font 1.125rem

All: border-radius 12px, font-weight 600, transition 0.2s
```

#### Badge
```
Variants:
- Blood Group: Rounded pill, bg varies by group, text white, font-mono
  O+: #FD6666, A+: #41A7F1, B+: #FCAA49, AB+: #AE41F1
  O-: #FF5678, A-: #64FFE3, B-: #29D64F, AB-: #FFFFFF

- Status: Rounded pill, dot + text
  Active: green dot + green text
  Pending: orange dot + orange text
  Urgent: red dot + red text
  Confirmed: teal dot + teal text
  Declined: pink dot + muted text
```

#### CountdownTimer
```
┌────────────────────────────┐
│  ⏱ 3 days 14:22:08       │
│  Transfusion Urgency       │
└────────────────────────────┘
Font: mono, Size: 1.5rem
Color changes: >7 days green, 3-7 days orange, <3 days red
Pulse animation when <3 days
Background: bg-card with colored left border (4px)
```

#### ProgressBar
```
┌──────────────────────────────────┐
│  ████████████░░░░░░░░  60%      │
│  3 of 5 donors confirmed        │
└──────────────────────────────────┘
Track: bg-surface, height 8px, border-radius 4px
Fill: gradient from --red to --teal
Label below: text-secondary, 0.875rem
```

---

### Page-Specific Components

#### Landing Page Components

##### HeroSection
```
┌──────────────────────────────────────────────────────────┐
│                                                           │
│           [Heart Icon]  PRAAN AI  ×  Blood Warriors      │
│                                                           │
│    AI-Powered Blood Coordination                          │
│    for Thalassemia Fighters                               │
│                                                           │
│    [See the Demo →]  [Learn More]                         │
│                                                           │
│    ┌──────────────────────────────────────────────────┐   │
│    │ 5,596 Donors │ 4,366 Collections │ 2M+ Reach    │   │
│    └──────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
Background: gradient from bg-primary to dark red
Title: 3.5rem, gradient text (red to orange)
Subtitle: 1.25rem, text-secondary
Buttons: Primary + Ghost, side by side
Stats bar: 3 StatCards in a row
```

##### DifferentiatorCard
```
┌────────────────────────────┐
│  [Icon]                     │
│                             │
│  Blood Bank Automation      │
│                             │
│  Check blood banks first.   │
│  Search, reserve, track     │
│  expiry — all automatic.    │
│                             │
│  [Try Demo →]               │
│                             │
│  AWS: DynamoDB + Lambda     │
└────────────────────────────┘
3 cards in a grid row
Each card: bg-card, hover scale(1.02)
Icon: 48px, colored circle bg
Title: 1.25rem, 700 weight
Description: text-secondary, 2-3 lines
CTA: text-link style (--blue)
AWS badge: small purple pill at bottom
```

---

#### Patient Onboarding Components

##### PatientForm
```
┌──────────────────────────────────────────┐
│  Patient Registration                     │
│                                           │
│  Name: [________________________]         │
│  Age: [________] Blood Group: [O+ ▼]     │
│  Location: [____________________]         │
│  Last Transfusion: [____/____/____]       │
│  Cycle Length: [____] days                │
│                                           │
│  Medical Report: [Upload PDF/Image]       │
│  ┌────────────────────────────────────┐   │
│  │ 📄 Drag & drop or click to upload │   │
│  └────────────────────────────────────┘   │
│                                           │
│  [Register Patient →]                     │
└──────────────────────────────────────────┘
Layout: 2-column grid on desktop, single column on mobile
Inputs: bg-surface, border, focus border-focus
Blood group: dropdown with colored options
Upload: dashed border, bg-surface, hover highlight
Submit: Primary button, full width
```

##### UrgencyWindow
```
┌──────────────────────────────────────────────────────┐
│  ⚡ Transfusion Urgency Window                        │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Patient: Kavya, 8 yrs, O+                      │ │
│  │                                                   │ │
│  │  ⏱ 3 DAYS 14:22:08  remaining                   │ │
│  │  ████████████░░░░░░░░░░░░░░  25%                 │ │
│  │                                                   │ │
│  │  Medical Report Values:                           │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐               │ │
│  │  │ Hb     │ │ MCV    │ │Ferritin│               │ │
│  │  │ 6.8    │ │ 62     │ │ 12     │               │ │
│  │  │ g/dL ↓ │ │ fL ↓   │ │ ng/mL↓│               │ │
│  │  └────────┘ └────────┘ └────────┘               │ │
│  │                                                   │ │
│  │  Priority: URGENT (within 3 days)                 │ │
│  │  Action: Donor search started NOW                 │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  [Start Donor Search →]  [View Blood Banks →]         │
└──────────────────────────────────────────────────────┘
Background: bg-card with red left border (4px) when urgent
Countdown: mono font, large (2rem), red when <3 days
Medical values: 3 mini-cards, red arrow down for low values
Priority: badge component (red/orange/green)
```

---

#### Blood Bank Components

##### InventoryTable
```
┌──────────────────────────────────────────────────────────┐
│  Blood Bank Inventory                 [Search] [Filter]  │
│                                                           │
│  ┌─────┬────────────┬────────┬───────┬────────┬────────┐│
│  │Bank │ Location   │ O+     │ A+    │ Expiry │ Action ││
│  ├─────┼────────────┼────────┼───────┼────────┼────────┤│
│  │Apollo│ Hyderabad │ 5 units│3 units│ Oct 15 │Reserve ││
│  │NIMS  │ Hyderabad │ 4 units│ -     │ Sep 28 │Reserve ││
│  │RedX  │ Secunderab│ -      │2 units│ Oct 02 │Reserve ││
│  └─────┴────────────┴────────┴───────┴────────┴────────┘│
│                                                           │
│  Total: O+: 23 units | A+: 15 units | B+: 18 units       │
└──────────────────────────────────────────────────────────┘
Table: bg-card rows, alternating bg-surface
Expiry column: red text if <7 days, orange if <14 days
Reserve button: secondary variant, small
Search: input with icon, filters blood_group + district
```

##### BloodBankCard (Mobile/Detail view)
```
┌────────────────────────────┐
│  🏥 Apollo Blood Bank      │
│  📍 Hyderabad, Telangana   │
│                             │
│  ┌────┐ ┌────┐ ┌────┐     │
│  │ O+ │ │ A+ │ │ B+ │     │
│  │  5 │ │  3 │ │  2 │     │
│  └────┘ └────┘ └────┘     │
│                             │
│  ⚠️ B+ expires in 5 days   │
│                             │
│  [Reserve O+] [View All]   │
└────────────────────────────┘
Card: bg-card, 16px radius
Blood group badges: colored pills with unit count
Expiry alert: orange background, warning icon
```

---

#### Voice Call Components

##### CallGrid (20 calls view)
```
┌──────────────────────────────────────────────────────────┐
│  📞 Voice Call Campaign — Patient: Kavya (O+, 3 days)    │
│                                                           │
│  Status: 3/20 Confirmed — 2 more needed                  │
│  ████████████░░░░░░░░░░░░░░░░░░░░  60%                  │
│                                                           │
│  [Start All Calls]                    [Cancel Remaining]  │
│                                                           │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Ravi  │ │Suresh│ │Priya │ │Amit  │ │Deepa │          │
│  │O+    │ │O+    │ │O+    │ │O+    │ │O+    │          │
│  │2.1km │ │3.4km │ │5.2km │ │6.1km │ │7.3km │          │
│  │ ✅   │ │ ✅   │ │ 📞   │ │ ✅   │ │ ❌   │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Kiran │ │Laksh │ │Manoj │ │Neha  │ │Omar  │          │
│  │O+    │ │O+    │ │O+    │ │O+    │ │O+    │          │
│  │8.0km │ │9.1km │ │10km  │ │11km  │ │12km  │          │
│  │ 🔄   │ │ 🔄   │ │ ⏳   │ │ ⏳   │ │ ⏳   │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│  (Row 3 and Row 4 similar...)                            │
└──────────────────────────────────────────────────────────┘
Grid: 5 columns × 4 rows
Each CallCard: 140px wide, bg-card
Status indicators:
  ⏳ Pending (gray)
  🔄 Calling (blue, pulse animation)
  ✅ Confirmed (teal, glow)
  ❌ Declined (pink)
  📞 Connected/In Progress (green, pulse)
  ⚡ No Answer (orange)
```

##### CallCard (Individual)
```
┌──────────────┐
│ Ravi Kumar   │
│ O+    2.1km  │
│ Score: 0.92  │
│              │
│    ✅        │
│  CONFIRMED   │
│              │
│ 12:04:32 PM  │
└──────────────┘
Width: 140px, Height: 180px
Background: bg-card, border colored by status
Name: 0.875rem, 600 weight
Blood group: colored badge
Distance: text-muted
Score: text-secondary
Status: large icon + label, centered
Timestamp: text-muted, 0.75rem
Animations: confirmed → teal glow, declined → fade out
```

---

#### Coordinator Command Center Components

##### WorkflowTimeline
```
┌──────────────────────────────────────────────────────────┐
│  Workflow: Kavya (O+, 2 units needed)                     │
│                                                           │
│  ● Patient Registered ────── ✅ 12:00 PM                 │
│  │                                                       │
│  ● Medical Report Scanned ─── ✅ 12:01 PM                 │
│  │  Hb: 6.8, Ferritin: 12                                 │
│  │                                                       │
│  ● Urgency Calculated ─────── ✅ 12:01 PM                 │
│  │  3 days remaining — URGENT                             │
│  │                                                       │
│  ● Blood Bank Search ──────── ✅ 12:02 PM                 │
│  │  Apollo: 2 units reserved                              │
│  │  Need 0 more from donors                               │
│  │                                                       │
│  ● Workflow Complete ──────── ✅ 12:02 PM                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
Timeline: vertical line (2px, --border) with nodes
Completed: green filled circle, teal line
Active: blue pulsing circle
Pending: gray empty circle
Each step: card with details, timestamp right-aligned
```

##### DonorRankList
```
┌──────────────────────────────────────────────────────────┐
│  Top Donors for O+ in Hyderabad                           │
│                                                           │
│  #1 Ravi Kumar    O+  Score: 0.92  2.1km  ✅ Confirmed   │
│  #2 Suresh M      O+  Score: 0.88  3.4km  ✅ Confirmed   │
│  #3 Priya S       O+  Score: 0.85  5.2km  📞 Calling     │
│  #4 Amit R        O+  Score: 0.82  6.1km  ✅ Confirmed   │
│  #5 Deepa V       O+  Score: 0.79  7.3km  ❌ Declined    │
│  ...                                                      │
│                                                           │
│  Readiness Score = Eligibility × Reliability × Proximity  │
└──────────────────────────────────────────────────────────┘
List: bg-card rows, hover highlight
Rank: mono font, colored (#1 gold, #2 silver, #3 bronze)
Score: progress bar, 0-1 scale
Status: badge component
```

##### FailureInsights
```
┌──────────────────────────────────────────────────────────┐
│  🧠 Self-Learning Insights                                │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Pattern: O+ requests in Hyderabad fail 40% in       │ │
│  │ Tier 1. System now starts with Tier 2 for this      │ │
│  │ combination. Success rate improved 23%.             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Pattern: Donors respond 35% better to calls made    │ │
│  │ between 6-8 PM. Campaign scheduler adjusted.        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Pattern: B- blood group has lowest donor density.    │ │
│  │ Expanded search radius from 10km to 25km for B-.   │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
Background: bg-card with purple left border (AI/intelligence color)
Each insight: mini-card, bg-surface
Pattern icon: 🧠 (brain) or ⚡ (lightning)
Improvement metrics: green text
```

---

## Page Layouts

### Landing Page (`/`)
```
[Navbar]
[HeroSection — full viewport height]
[DifferentiatorCards — 3 columns grid]
[StatsBar — 4 StatCards in row]
[HowItWorks — 5 step visual flow]
[TechStack — AWS services grid]
[Footer]
```

### Patient Onboarding (`/patient`)
```
[Navbar]
[PageHeader — "Patient Onboarding"]
[2-column layout:
  Left: PatientForm
  Right: UrgencyWindow (appears after registration)
]
[PatientList — existing patients table]
[Footer]
```

### Blood Bank (`/blood-bank`)
```
[Navbar]
[PageHeader — "Blood Bank Inventory"]
[StatsRow — total units per blood group]
[SearchBar + Filters]
[InventoryTable]
[ExpiryAlerts — expiring stock warnings]
[Footer]
```

### Voice Call Dashboard (`/donor-outreach`)
```
[Navbar]
[PageHeader — "AI Voice Call Campaign"]
[CampaignInfo — patient name, blood group, units needed]
[ProgressSection — confirmed/target progress bar]
[CallGrid — 5×4 grid of CallCards]
[ActionButtons — Start All / Cancel Remaining]
[Footer]
```

### Coordinator Command Center (`/coordinator`)
```
[Navbar]
[PageHeader — "Coordinator Command Center"]
[3-column layout:
  Left: ActiveWorkflows (list)
  Center: WorkflowTimeline (selected workflow)
  Right: DonorRankList + FailureInsights
]
[ActivityFeed — real-time log at bottom]
[Footer]
```

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|-----------|-------|----------------|
| Mobile | < 640px | Single column, stacked cards, hamburger nav |
| Tablet | 640-1024px | 2 columns, scrollable tables |
| Desktop | 1024-1440px | Full layout, 3 columns |
| Wide | > 1440px | Max-width 1280px, centered |

---

## Animation Patterns

| Component | Animation | Duration |
|-----------|----------|----------|
| Card hover | scale(1.02) + shadow increase | 0.2s ease |
| CallCard status change | color transition + glow | 0.3s ease |
| CountdownTimer (< 3 days) | pulse border red | 1s infinite |
| ProgressBar fill | width transition | 0.5s ease |
| WorkflowTimeline step | slide in from left | 0.3s ease |
| Page transition | fade in | 0.2s ease |
| Button click | scale(0.98) | 0.1s ease |
| CallCard calling status | border pulse blue | 1.5s infinite |
