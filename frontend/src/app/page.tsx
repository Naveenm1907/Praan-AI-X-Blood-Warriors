"use client";

import Link from "next/link";
import { Heart, Hospital, Clock, Phone } from "@phosphor-icons/react";
import { Button } from "@/components/Button";

export default function Home() {
  return (
    <div className="relative">
      {/* Noise overlay */}
      <div className="noise-overlay" />

      {/* Hero - Dramatic editorial style */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        <div className="mx-auto max-w-7xl px-6 py-32 w-full">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            {/* Left: Massive title */}
            <div className="md:col-span-8 relative">
              <div className="mb-4 flex items-center gap-3">
                <Heart className="text-blood" size={24} weight="fill" />
                <span className="text-sm uppercase tracking-widest text-[var(--blood-pink)] font-medium">
                  Blood Warriors × AI
                </span>
              </div>
              <h1 className="editorial text-7xl md:text-8xl lg:text-9xl font-bold mb-8">
                <span className="block">PRAAN</span>
                <span className="block text-[var(--blood-pink)]">AI</span>
              </h1>
              <p className="text-xl md:text-2xl text-[var(--text-secondary)] max-w-2xl mb-12 leading-relaxed">
                Autonomous blood coordination network. <br className="hidden md:block" />
                <span className="text-[var(--text-primary)] font-medium">2 hours of coordination in 5 minutes.</span>
              </p>
              <div className="flex flex-wrap gap-4">
                <Link href="/admin/coordinator">
                  <Button variant="primary">
                    Launch Dashboard
                  </Button>
                </Link>
                <Link href="/patient">
                  <Button variant="editorial">
                    Onboard Patient
                  </Button>
                </Link>
              </div>
            </div>

            {/* Right: Dramatic stat */}
            <div className="md:col-span-4 md:ml-auto">
              <div className="bg-[var(--blood-pink)] text-white p-8 -mr-6 md:-mr-12">
                <div className="text-6xl md:text-7xl font-bold mb-2">5,596</div>
                <div className="text-sm uppercase tracking-wider opacity-90">Registered Donors</div>
                <div className="mt-6 pt-6 border-t border-white/20">
                  <div className="text-2xl font-bold mb-1">4,366</div>
                  <div className="text-xs uppercase tracking-wider opacity-90">Collections</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats - Asymmetric editorial layout */}
      <section className="py-32 border-t border-[var(--border)]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
            <div className="col-span-2">
              <div className="text-6xl md:text-7xl font-bold text-[var(--text-primary)] mb-2">1,34,000+</div>
              <div className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">Lives Touched</div>
              <div className="accent-bar mt-4" />
            </div>
            <div>
              <div className="text-4xl md:text-5xl font-bold text-[var(--text-primary)] mb-2">2M+</div>
              <div className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">Digital Reach</div>
            </div>
            <div>
              <div className="text-4xl md:text-5xl font-bold text-[var(--blood-pink)] mb-2">5min</div>
              <div className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">Average Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* Differentiators - Broken grid editorial */}
      <section className="py-32 border-t border-[var(--border)]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-20">
            <div className="accent-bar mb-6" />
            <h2 className="editorial text-5xl md:text-6xl font-bold mb-6">
              Three Differentiators
            </h2>
            <p className="text-xl text-[var(--text-secondary)] max-w-2xl">
              Other teams start with donor search. We check blood banks first,
              calculate urgency from medical data, and call 20 donors at once.
            </p>
          </div>

          {/* Feature 1 - Full width */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 mb-20 pb-20 border-b border-[var(--border)]">
            <div className="md:col-span-5">
              <div className="sticky top-32">
                <div className="inline-block px-4 py-2 bg-[var(--blood-pink)]/10 text-[var(--blood-pink)] text-sm uppercase tracking-wider mb-6">
                  01
                </div>
                <h3 className="text-3xl md:text-4xl font-bold mb-4">Blood Bank Automation</h3>
                <p className="text-lg text-[var(--text-secondary)] mb-6">
                  Check blood banks first. Auto-search by blood group and district, reserve units instantly, track expiry dates.
                </p>
                <Link href="/blood-bank" className="inline-flex items-center gap-2 text-[var(--blood-pink)] hover:gap-3 transition-all">
                  <span className="font-medium">View Inventory</span>
                  <span>→</span>
                </Link>
              </div>
            </div>
            <div className="md:col-span-7">
              <div className="bg-[var(--bg-surface)] p-8 md:p-12">
                <Hospital size={48} weight="regular" className="text-[var(--blood-pink)] mb-6" />
                <div className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-2">AWS Stack</div>
                <div className="text-lg font-mono text-[var(--text-primary)]">
                  DynamoDB + Lambda + S3
                </div>
                <div className="mt-8 pt-8 border-t border-[var(--border)]">
                  <p className="text-[var(--text-secondary)]">
                    Donors are the last resort, not the first. We check 30+ blood banks before activating donor search.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Feature 2 - Two columns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="pb-12 border-b md:border-b-0 md:border-r border-[var(--border)] md:pr-12">
              <div className="inline-block px-4 py-2 bg-[var(--orange)]/10 text-[var(--orange)] text-sm uppercase tracking-wider mb-6">
                02
              </div>
              <Clock size={40} weight="regular" className="text-[var(--orange)] mb-4" />
              <h3 className="text-2xl md:text-3xl font-bold mb-4">Transfusion Urgency Window</h3>
              <p className="text-[var(--text-secondary)] mb-6">
                Upload a medical report and the AI reads Hb, MCV, ferritin values. Calculates exactly how many days the patient can wait.
              </p>
              <div className="flex items-center justify-between mb-6">
                <Link href="/patient" className="inline-flex items-center gap-2 text-[var(--orange)] hover:gap-3 transition-all">
                  <span className="font-medium">Onboard Patient</span>
                  <span>→</span>
                </Link>
                <span className="text-xs uppercase tracking-wider text-[var(--text-secondary)]">
                  Textract + SageMaker
                </span>
              </div>
            </div>

            <div className="pb-12">
              <div className="inline-block px-4 py-2 bg-[var(--info)]/10 text-[var(--info)] text-sm uppercase tracking-wider mb-6">
                03
              </div>
              <Phone size={40} weight="regular" className="text-[var(--info)] mb-4" />
              <h3 className="text-2xl md:text-3xl font-bold mb-4">AI Voice Call Assistant</h3>
              <p className="text-[var(--text-secondary)] mb-6">
                Calls 20 donors simultaneously in their language. Polly speaks, Lex listens, dashboard updates live.
              </p>
              <div className="flex items-center justify-between">
                <Link href="/donor-outreach" className="inline-flex items-center gap-2 text-[var(--info)] hover:gap-3 transition-all">
                  <span className="font-medium">Start Campaign</span>
                  <span>→</span>
                </Link>
                <span className="text-xs uppercase tracking-wider text-[var(--text-secondary)]">
                  Connect + Polly + Lex
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow - Vertical editorial timeline */}
      <section className="py-32 bg-[var(--blood-pink)] text-white">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16">
            <h2 className="editorial text-5xl md:text-6xl font-bold mb-6">
              The Workflow
            </h2>
            <p className="text-xl opacity-90 max-w-2xl">
              Seven steps from patient registration to confirmed donors. Fully automated.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-8">
            {[
              { step: "01", label: "Patient Onboards", detail: "Upload medical report" },
              { step: "02", label: "AI Reads Report", detail: "OCR extracts Hb, MCV, ferritin" },
              { step: "03", label: "Urgency Calculated", detail: "Countdown timer starts" },
              { step: "04", label: "Blood Bank Check", detail: "Search, reserve, or skip" },
              { step: "05", label: "Donors Ranked", detail: "Readiness score from 5 signals" },
              { step: "06", label: "20 Parallel Calls", detail: "AI speaks in donor language" },
              { step: "07", label: "Donors Confirmed", detail: "Remaining calls auto-cancel" },
            ].map((s, i) => (
              <div
                key={s.step}
                className={`flex gap-6 ${i % 2 === 0 ? 'md:translate-y-0' : 'md:translate-y-12'}`}
              >
                <div className="text-4xl font-bold opacity-50">{s.step}</div>
                <div>
                  <div className="text-xl font-bold mb-1">{s.label}</div>
                  <div className="text-sm opacity-90">{s.detail}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack - Editorial list */}
      <section className="py-32 border-t border-[var(--border)]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-12">
            <div className="md:col-span-4">
              <div className="sticky top-32">
                <div className="accent-bar mb-6" />
                <h2 className="editorial text-4xl md:text-5xl font-bold mb-4">
                  Built on AWS
                </h2>
                <p className="text-lg text-[var(--text-secondary)]">
                  Enterprise-grade infrastructure for mission-critical blood coordination.
                </p>
              </div>
            </div>
            <div className="md:col-span-8">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-px bg-[var(--border)]">
                {[
                  "DynamoDB", "Lambda", "API Gateway", "S3",
                  "Bedrock", "SageMaker", "Textract", "Polly",
                  "Amazon Connect", "Lex", "SNS", "CloudWatch",
                ].map((service) => (
                  <div
                    key={service}
                    className="bg-[var(--bg-primary)] p-6 text-center hover:bg-[var(--bg-surface)] transition-colors"
                  >
                    <div className="text-sm font-mono text-[var(--text-primary)]">{service}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
