import Link from "next/link";

const stats = [
  { value: "5,596", label: "Registered Donors" },
  { value: "4,366", label: "Blood Collections" },
  { value: "1,34,000+", label: "Lives Touched" },
  { value: "2M+", label: "Digital Reach" },
];

const differentiators = [
  {
    icon: "🏥",
    title: "Blood Bank Automation",
    description:
      "Check blood banks first. Auto-search by blood group and district, reserve units instantly, track expiry dates. Donors are the last resort, not the first.",
    cta: "/blood-bank",
    ctaLabel: "View Inventory",
    aws: "DynamoDB + Lambda + S3",
    color: "var(--blood)",
  },
  {
    icon: "⏱",
    title: "Transfusion Urgency Window",
    description:
      "Upload a medical report and the AI reads Hb, MCV, ferritin values. Calculates exactly how many days the patient can wait. No guessing, no severity labels — just a countdown.",
    cta: "/patient",
    ctaLabel: "Onboard Patient",
    aws: "Textract + SageMaker + Bedrock",
    color: "var(--orange)",
  },
  {
    icon: "📞",
    title: "AI Voice Call Assistant",
    description:
      "Calls 20 donors simultaneously in their language. Polly speaks, Lex listens, dashboard updates live. A 2-hour coordinator task done in 5 minutes.",
    cta: "/donor-outreach",
    ctaLabel: "Start Campaign",
    aws: "Connect + Polly + Lex + Lambda",
    color: "var(--blue)",
  },
];

const workflowSteps = [
  { step: "1", label: "Patient Onboards", detail: "Upload medical report" },
  { step: "2", label: "AI Reads Report", detail: "OCR extracts Hb, MCV, ferritin" },
  { step: "3", label: "Urgency Calculated", detail: "Countdown timer starts" },
  { step: "4", label: "Blood Bank Check", detail: "Search, reserve, or skip" },
  { step: "5", label: "Donors Ranked", detail: "Readiness score from 5 signals" },
  { step: "6", label: "20 Parallel Calls", detail: "AI speaks in donor language" },
  { step: "7", label: "Donors Confirmed", detail: "Remaining calls auto-cancel" },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--blood)]/10 to-transparent" />
        <div className="relative mx-auto max-w-7xl px-6 py-24 text-center">
          <div className="mb-6 flex items-center justify-center gap-3">
            <span className="text-4xl text-blood">&#9829;</span>
            <h1 className="text-4xl font-bold tracking-tight text-[var(--text-primary)] sm:text-5xl">
              PRAAN AI
            </h1>
            <span className="text-2xl text-[var(--text-muted)]">&times;</span>
            <span className="text-2xl font-semibold text-[var(--orange)]">
              Blood Warriors
            </span>
          </div>

          <p className="mx-auto max-w-2xl text-xl text-[var(--text-secondary)]">
            AI-Powered Blood Coordination for Thalassemia Fighters.
            Every drop counts. Every second matters.
          </p>

          <div className="mt-8 flex items-center justify-center gap-4">
            <Link
              href="/coordinator"
              className="rounded-xl bg-blood px-8 py-3 text-base font-semibold text-white transition-all hover:brightness-110"
            >
              See the Demo
            </Link>
            <Link
              href="/patient"
              className="rounded-xl border border-blood px-8 py-3 text-base font-semibold text-blood transition-all hover:bg-blood/10"
            >
              Onboard Patient
            </Link>
          </div>

          {/* Stats */}
          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-4">
            {stats.map((s) => (
              <div
                key={s.label}
                className="rounded-2xl border border-border bg-card p-6"
              >
                <p className="text-2xl font-bold text-[var(--text-primary)]">
                  {s.value}
                </p>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  {s.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Differentiators */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <h2 className="mb-4 text-center text-3xl font-bold">
          What Makes Us Different
        </h2>
        <p className="mx-auto mb-12 max-w-xl text-center text-[var(--text-secondary)]">
          Other teams start with donor search. We check blood banks first,
          calculate urgency from medical data, and call 20 donors at once.
        </p>

        <div className="grid gap-6 md:grid-cols-3">
          {differentiators.map((d) => (
            <div
              key={d.title}
              className="group rounded-2xl border border-border bg-card p-8 transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-black/30"
            >
              <div
                className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl text-2xl"
                style={{ background: `${d.color}20` }}
              >
                {d.icon}
              </div>
              <h3 className="mb-2 text-xl font-bold">{d.title}</h3>
              <p className="mb-6 text-sm leading-relaxed text-[var(--text-secondary)]">
                {d.description}
              </p>
              <Link
                href={d.cta}
                className="text-sm font-semibold text-info transition-colors hover:underline"
              >
                {d.ctaLabel} &rarr;
              </Link>
              <div className="mt-4 inline-block rounded-full bg-[var(--ai)]/15 px-3 py-1 text-xs text-[var(--ai)]">
                {d.aws}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section className="bg-[var(--bg-surface)] py-20">
        <div className="mx-auto max-w-7xl px-6">
          <h2 className="mb-12 text-center text-3xl font-bold">
            How PRAAN AI Works
          </h2>
          <div className="flex flex-wrap items-start justify-center gap-4">
            {workflowSteps.map((s, i) => (
              <div key={s.step} className="flex items-center gap-4">
                <div className="w-36 text-center">
                  <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-blood/20 text-lg font-bold text-blood">
                    {s.step}
                  </div>
                  <p className="text-sm font-semibold">{s.label}</p>
                  <p className="text-xs text-[var(--text-muted)]">{s.detail}</p>
                </div>
                {i < workflowSteps.length - 1 && (
                  <span className="text-[var(--text-muted)]">&rarr;</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold">
          Built on AWS
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
          {[
            "DynamoDB", "Lambda", "API Gateway", "S3",
            "Bedrock", "SageMaker", "Textract", "Polly",
            "Amazon Connect", "Lex", "SNS", "CloudWatch",
          ].map((service) => (
            <div
              key={service}
              className="rounded-xl border border-border bg-card px-4 py-3 text-center text-sm font-medium text-[var(--text-secondary)]"
            >
              {service}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
