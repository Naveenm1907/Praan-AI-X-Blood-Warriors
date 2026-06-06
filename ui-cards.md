# PRAAN AI — UI Card Specifications

> Design System × Component Library × Page Layouts
> Blood Warriors Brand Colors × Dark Theme × Card-Based UI

---

## Design System

### Color Palette
```css
/* Primary */
--red:        oklch(0.65 0.18 25);     /* Blood/action */
--orange:     oklch(0.72 0.15 55);     /* Warning/urgency */
--blue:       oklch(0.68 0.14 240);    /* Info/calling */
--teal:       oklch(0.78 0.12 175);    /* Success/confirmed */
--pink:       oklch(0.62 0.19 10);     /* Highlight/important */
--green:      oklch(0.68 0.16 145);    /* Positive/available */

/* Backgrounds (Dark Theme) */
--bg-primary:   oklch(0.15 0.008 25);
--bg-card:      oklch(0.20 0.008 25);
--bg-card-hover:oklch(0.25 0.008 25);
--bg-surface:   oklch(0.17 0.008 25);

/* Text */
--text-primary:   oklch(0.98 0.005 25);
--text-secondary: oklch(0.72 0.008 25);
--text-muted:     oklch(0.52 0.008 25);

/* Borders */
--border:       oklch(0.28 0.008 25);
--border-focus: oklch(0.68 0.14 240);
```

### Typography
- **Display/Headlines**: Satoshi, 700 weight
- **Body**: Spectral, 400 weight
- **Mono/Data**: JetBrains Mono (countdown timers, scores, metrics)
- **Scale**:
  - Display: 3.5rem, tracking-tighter, leading-none
  - H1: 2.5rem, tracking-tight
  - H2: 2rem, tracking-tight
  - H3: 1.5rem
  - Body: 1rem, leading-relaxed, max-width 65ch
  - Small: 0.875rem
  - Caption: 0.75rem

### Spacing
- Base unit: 4px
- Card padding: 24px (p-6)
- Section gap: 48px (varied for rhythm, not uniform)
- Grid gap: 16px
- Component gap: 8px

### Border Radius
- Cards: 16px (rounded-2xl)
- Buttons: 10px (rounded-lg)
- Inputs: 8px (rounded-md)
- Badges: 6px (rounded-md)
- Avatars: 50% (full round)

### Shadows (tinted to background)
```css
--shadow-card: 0 4px 24px -8px oklch(0.15 0.008 25 / 0.4);
--shadow-hover: 0 8px 32px -8px oklch(0.15 0.008 25 / 0.5);
--shadow-subtle: 0 2px 8px -2px oklch(0.15 0.008 25 / 0.3);
```

---

## Component Inventory

### Layout Components

#### Navbar
```
┌──────────────────────────────────────────────────────────┐
│ [PRAAN AI] [Blood Warriors]    Home  Demo  About  Login  │
└──────────────────────────────────────────────────────────┘
Height: 64px, Background: bg-primary, Border-bottom: border
Logo: "PRAAN AI" text with heart icon (--red) + separator + Blood Warriors text
Nav links: text-secondary, hover: text-primary
Active link: text-primary + underline (--red, 2px)
```

#### Footer
```
┌──────────────────────────────────────────────────────────┐
│ PRAAN AI [Blood Warriors]                                │
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
Hover: bg-card-hover + shadow-hover + translate-y-[-1px]
Transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1)
```

#### StatCard
```
┌──────────────────────┐
│  [Icon] 5,596        │
│  Registered Donors   │
│  +12% this month     │
└──────────────────────┘
Top: Icon (40px circle, colored background with 10% opacity)
Middle: Value (2rem, 700 weight, text-primary, font-mono)
Bottom: Label (0.875rem, text-secondary)
Optional: Trend badge (green/red, 0.75rem)
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

All: border-radius 10px, font-weight 600
Hover: translate-y-[-1px]
Active: translate-y-[1px] or scale-[0.98]
Transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1)
```

#### Badge
```
Variants:
- Blood Group: Rounded pill, bg varies by group (10% opacity), text colored, font-mono
  O+: --red, A+: --blue, B+: --orange, AB+: purple
  O-: --pink, A-: --teal, B-: --green, AB-: text-primary

- Status: Rounded pill, dot + text
  Active: green dot + green text
  Pending: orange dot + orange text
  Urgent: red dot + red text
  Confirmed: teal dot + teal text
  Declined: muted dot + muted text
```

#### CountdownTimer
```
┌────────────────────────────┐
│  [Clock Icon] 3d 14:22:08  │
│  Transfusion Urgency       │
└────────────────────────────┘
Font: mono, Size: 1.5rem
Color changes: >7 days green, 3-7 days orange, <3 days red
Pulse animation when <3 days (border opacity 0.3 → 0.6)
Background: bg-card with top border (4px, colored by urgency)
```

#### ProgressBar
```
┌──────────────────────────────────┐
│  ████████████░░░░░░░░  60%      │
│  3 of 5 donors confirmed        │
└──────────────────────────────────┘
Track: bg-surface, height 8px, border-radius 4px
Fill: solid --teal (no gradient)
Label below: text-secondary, 0.875rem
Transition: width 0.5s cubic-bezier(0.16, 1, 0.3, 1)
```

---

### Page-Specific Components

#### Landing Page Components

##### HeroSection
```
┌──────────────────────────────────────────────────────────┐
│                                                           │
│  PRAAN AI                                                 │
│  [Blood Warriors]                                         │
│                                                           │
│  AI-Powered Blood Coordination                            │
│  for Thalassemia Fighters                                 │
│                                                           │
│  [See the Demo]  [Learn More]                             │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ 5,596 Donors │ 4,366 Collections │ 2M+ Reach    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
└──────────────────────────────────────────────────────────┘
Background: bg-primary (solid, no gradient)
Title: 3.5rem, tracking-tighter, text-primary (no gradient text)
Subtitle: 1.25rem, text-secondary, max-w-[65ch]
Layout: Left-aligned text, right side empty or subtle pattern
Buttons: Primary + Ghost, side by side
Stats bar: 3 StatCards in horizontal scroll on mobile, row on desktop
```

##### DifferentiatorCard
```
Desktop (2-column zig-zag):
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
┌────────────────────────────┐
│         [Icon]              │
│                             │
│      Urgency Window         │
│                             │
│   Calculate exactly how     │
│   many days patient can     │
│   wait for transfusion.     │
│                             │
│         [Try Demo →]        │
│                             │
│   AWS: Textract + Lambda    │
└────────────────────────────┘

Mobile: Single column stack

Each card: bg-card, hover scale(1.01) + shadow-hover
Icon: 48px, colored circle bg (10% opacity)
Title: 1.5rem, 700 weight
Description: text-secondary, max-w-[55ch]
CTA: text-link style (--blue), no underline, hover underline
AWS badge: small pill at bottom (bg-surface, text-muted)
```

---

#### Patient Onboarding Components

##### PatientForm
```
┌──────────────────────────────────────────┐
│  Patient Registration                     │
│                                           │
│  Name                                     │
│  [________________________]               │
│                                           │
│  Age          Blood Group                 │
│  [________]   [O+ ▼]                      │
│                                           │
│  Location                                 │
│  [____________________]                   │
│                                           │
│  Last Transfusion                         │
│  [____/____/____]                         │
│                                           │
│  Cycle Length (days)                      │
│  [____]                                   │
│                                           │
│  Medical Report                           │
│  ┌────────────────────────────────────┐   │
│  │ [Upload Icon]                      │   │
│  │ Drag & drop or click to upload    │   │
│  └────────────────────────────────────┘   │
│                                           │
│  [Register Patient →]                     │
└──────────────────────────────────────────┘
Layout: 2-column grid on desktop, single column on mobile
Inputs: bg-surface, border, focus border-focus + ring-2 ring-focus/20
Labels: Above inputs, text-secondary, 0.875rem, font-weight 500
Blood group: dropdown with colored options
Upload: dashed border, bg-surface, hover highlight
Submit: Primary button, full width
Error states: Red border + error text below input
```

##### UrgencyWindow
```
┌──────────────────────────────────────────────────────┐
│  [Lightning Icon] Transfusion Urgency Window         │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │  Patient: Kavya, 8 yrs, O+                      │ │
│  │                                                   │ │
│  │  3 DAYS 14:22:08  remaining                     │ │
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
Background: bg-card with top border (4px, red when urgent)
Countdown: mono font, large (2rem), red when <3 days
Medical values: 3 mini-cards in row, red arrow down for low values
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
│  [Hospital Icon] Apollo    │
│  [Pin Icon] Hyderabad      │
│                             │
│  ┌────┐ ┌────┐ ┌────┐     │
│  │ O+ │ │ A+ │ │ B+ │     │
│  │  5 │ │  3 │ │  2 │     │
│  └────┘ └────┘ └────┘     │
│                             │
│  [Warning Icon] B+ expires │
│  in 5 days                  │
│                             │
│  [Reserve O+] [View All]   │
└────────────────────────────┘
Card: bg-card, 16px radius
Blood group badges: colored pills with unit count
Expiry alert: orange background (10% opacity), warning icon
```

---

#### Voice Call Components

##### CallGrid (20 calls view)
```
┌──────────────────────────────────────────────────────────┐
│  [Phone Icon] Voice Call Campaign                        │
│  Patient: Kavya (O+, 3 days)                             │
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
│  │ CONF │ │ CONF │ │CALL  │ │ CONF │ │DECL  │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Kiran │ │Laksh │ │Manoj │ │Neha  │ │Omar  │          │
│  │O+    │ │O+    │ │O+    │ │O+    │ │O+    │          │
│  │8.0km │ │9.1km │ │10km  │ │11km  │ │12km  │          │
│  │PEND  │ │PEND  │ │WAIT  │ │WAIT  │ │WAIT  │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
└──────────────────────────────────────────────────────────┘
Grid: 5 columns × 4 rows (responsive: 3 cols tablet, 2 cols mobile)
Each CallCard: 140px wide, bg-card
Status indicators (text labels, not emojis):
  PENDING (muted)
  CALLING (blue, pulse border)
  CONFIRMED (teal)
  DECLINED (pink)
  CONNECTED (green, pulse border)
  NO ANSWER (orange)
```

##### CallCard (Individual)
```
┌──────────────┐
│ Ravi Kumar   │
│ O+    2.1km  │
│ Score: 0.92  │
│              │
│  CONFIRMED   │
│              │
│ 12:04:32 PM  │
└──────────────┘
Width: 140px, Height: 180px
Background: bg-card, border colored by status (2px)
Name: 0.875rem, 600 weight
Blood group: colored badge
Distance: text-muted, font-mono
Score: text-secondary, font-mono
Status: large text label, centered, colored
Timestamp: text-muted, 0.75rem, font-mono
Animations: confirmed → border pulse teal, declined → opacity 0.6
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
Active: blue pulsing circle (scale 1 → 1.1, infinite)
Pending: gray empty circle
Each step: card with details, timestamp right-aligned
```

##### DonorRankList
```
┌──────────────────────────────────────────────────────────┐
│  Top Donors for O+ in Hyderabad                           │
│                                                           │
│  #1 Ravi Kumar    O+  Score: 0.92  2.1km  CONFIRMED      │
│  #2 Suresh M      O+  Score: 0.88  3.4km  CONFIRMED      │
│  #3 Priya S       O+  Score: 0.85  5.2km  CALLING        │
│  #4 Amit R        O+  Score: 0.82  6.1km  CONFIRMED      │
│  #5 Deepa V       O+  Score: 0.79  7.3km  DECLINED       │
│  ...                                                      │
│                                                           │
│  Readiness Score = Eligibility × Reliability × Proximity  │
└──────────────────────────────────────────────────────────┘
List: bg-card rows, hover highlight
Rank: mono font, colored (#1 gold, #2 silver, #3 bronze)
Score: progress bar, 0-1 scale, font-mono
Status: badge component
```

##### FailureInsights
```
┌──────────────────────────────────────────────────────────┐
│  [Brain Icon] Self-Learning Insights                     │
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
Background: bg-card (no side-stripe border)
Each insight: mini-card, bg-surface
Pattern icon: [Brain Icon] from Phosphor/Radix (no emoji)
Improvement metrics: green text, font-mono
```

---

## Page Layouts

### Landing Page (`/`)
```
[Navbar]
[HeroSection — full viewport height, left-aligned]
[DifferentiatorCards — 2-column zig-zag on desktop, stack on mobile]
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
| Mobile | < 640px | Single column, stacked cards, hamburger nav, min-h-[100dvh] |
| Tablet | 640-1024px | 2 columns, scrollable tables |
| Desktop | 1024-1440px | Full layout, 3 columns |
| Wide | > 1440px | Max-width 1280px, centered |

---

## Animation Patterns

| Component | Animation | Duration | Easing |
|-----------|----------|----------|--------|
| Card hover | translate-y-[-1px] + shadow increase | 0.3s | cubic-bezier(0.16, 1, 0.3, 1) |
| CallCard status change | border color transition | 0.3s | cubic-bezier(0.16, 1, 0.3, 1) |
| CountdownTimer (< 3 days) | pulse border opacity | 1.5s | ease-in-out infinite |
| ProgressBar fill | width transition | 0.5s | cubic-bezier(0.16, 1, 0.3, 1) |
| WorkflowTimeline step | slide in from left | 0.3s | cubic-bezier(0.16, 1, 0.3, 1) |
| Page transition | fade in | 0.2s | ease-out |
| Button click | scale-[0.98] | 0.1s | ease-out |
| CallCard calling status | border pulse blue | 1.5s | ease-in-out infinite |
| List stagger | opacity + translate-y | 0.3s | cubic-bezier(0.16, 1, 0.3, 1) + delay |

---

## Icon System

Use Phosphor Icons or Radix Icons (no emojis):

```
Heart — PRAAN AI logo
Hospital — Blood bank
Phone — Voice calls
Clock — Urgency/timing
Lightning — Priority/urgent
Warning — Expiry/alerts
Brain — AI/intelligence
Upload — File upload
Search — Search
Filter — Filters
Pin — Location
Check — Confirmed
X — Declined/error
Arrow Right — CTA/navigation
```

All icons: 1.5px stroke width, consistent across app.

---

## Accessibility

- **Contrast**: All text meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
- **Focus states**: Visible ring-2 ring-focus/20 on all interactive elements
- **Reduced motion**: Respect `prefers-reduced-motion` (disable animations)
- **Color blindness**: Don't rely on color alone (use icons + text labels)
- **Keyboard navigation**: All interactive elements reachable via Tab
- **Screen readers**: Proper ARIA labels, semantic HTML

---

## Performance

- **Hardware acceleration**: Animate only `transform` and `opacity`
- **Lazy loading**: Images and heavy components use `loading="lazy"`
- **Code splitting**: Route-based code splitting
- **Font loading**: `font-display: swap` for web fonts
- **Image optimization**: WebP format, responsive srcset

---

## Design Tokens Export

```json
{
  "color": {
    "red": "oklch(0.65 0.18 25)",
    "orange": "oklch(0.72 0.15 55)",
    "blue": "oklch(0.68 0.14 240)",
    "teal": "oklch(0.78 0.12 175)",
    "pink": "oklch(0.62 0.19 10)",
    "green": "oklch(0.68 0.16 145)"
  },
  "background": {
    "primary": "oklch(0.15 0.008 25)",
    "card": "oklch(0.20 0.008 25)",
    "surface": "oklch(0.17 0.008 25)"
  },
  "text": {
    "primary": "oklch(0.98 0.005 25)",
    "secondary": "oklch(0.72 0.008 25)",
    "muted": "oklch(0.52 0.008 25)"
  },
  "border": {
    "default": "oklch(0.28 0.008 25)",
    "focus": "oklch(0.68 0.14 240)"
  },
  "spacing": {
    "base": "4px",
    "card": "24px",
    "section": "48px",
    "grid": "16px",
    "component": "8px"
  },
  "radius": {
    "card": "16px",
    "button": "10px",
    "input": "8px",
    "badge": "6px"
  },
  "typography": {
    "display": {
      "family": "Satoshi",
      "size": "3.5rem",
      "weight": 700,
      "tracking": "-0.05em"
    },
    "h1": {
      "family": "Satoshi",
      "size": "2.5rem",
      "weight": 700,
      "tracking": "-0.025em"
    },
    "body": {
      "family": "Spectral",
      "size": "1rem",
      "weight": 400,
      "lineHeight": 1.6,
      "maxWidth": "65ch"
    },
    "mono": {
      "family": "JetBrains Mono",
      "size": "1rem",
      "weight": 400
    }
  },
  "shadow": {
    "card": "0 4px 24px -8px oklch(0.15 0.008 25 / 0.4)",
    "hover": "0 8px 32px -8px oklch(0.15 0.008 25 / 0.5)",
    "subtle": "0 2px 8px -2px oklch(0.15 0.008 25 / 0.3)"
  },
  "animation": {
    "ease": "cubic-bezier(0.16, 1, 0.3, 1)",
    "duration": {
      "fast": "0.1s",
      "normal": "0.3s",
      "slow": "0.5s"
    }
  }
}
```
