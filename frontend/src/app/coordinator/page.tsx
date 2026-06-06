"use client";

import { useState } from "react";
import type { WorkflowStep, BloodGroup } from "@/lib/types";
import { BLOOD_GROUP_COLORS } from "@/lib/types";

interface ActiveWorkflow {
  id: string;
  patient_name: string;
  blood_group: BloodGroup;
  urgency_days: number;
  current_step: string;
  steps: WorkflowStep[];
  status: "active" | "completed";
}

const workflows: ActiveWorkflow[] = [
  {
    id: "wf001",
    patient_name: "Kavya Reddy",
    blood_group: "O+",
    urgency_days: 3,
    current_step: "donor_outreach",
    status: "active",
    steps: [
      { step_name: "Patient Registered", status: "completed", started_at: "12:00 PM", completed_at: "12:00 PM", details: "Age 8, Thalassemia Major" },
      { step_name: "Medical Report Scanned", status: "completed", started_at: "12:01 PM", completed_at: "12:01 PM", details: "Hb: 6.8, Ferritin: 12, MCV: 62" },
      { step_name: "Urgency Calculated", status: "completed", started_at: "12:01 PM", completed_at: "12:01 PM", details: "3 days remaining — URGENT" },
      { step_name: "Blood Bank Search", status: "completed", started_at: "12:02 PM", completed_at: "12:03 PM", details: "Apollo: 2 units reserved" },
      { step_name: "Donor Outreach", status: "active", started_at: "12:03 PM", details: "20 parallel calls — 3/5 confirmed" },
      { step_name: "Donors Confirmed", status: "pending" },
    ],
  },
  {
    id: "wf002",
    patient_name: "Arjun S",
    blood_group: "O-",
    urgency_days: 2,
    current_step: "blood_bank_search",
    status: "active",
    steps: [
      { step_name: "Patient Registered", status: "completed", started_at: "11:30 AM", completed_at: "11:30 AM", details: "Age 10, Sickle Cell" },
      { step_name: "Medical Report Scanned", status: "completed", started_at: "11:31 AM", completed_at: "11:32 AM", details: "Hb: 5.9, Ferritin: 8, MCV: 55" },
      { step_name: "Urgency Calculated", status: "completed", started_at: "11:32 AM", completed_at: "11:32 AM", details: "2 days remaining — CRITICAL" },
      { step_name: "Blood Bank Search", status: "active", started_at: "11:33 AM", details: "Searching O- stock in Secunderabad..." },
      { step_name: "Donor Outreach", status: "pending" },
      { step_name: "Donors Confirmed", status: "pending" },
    ],
  },
  {
    id: "wf003",
    patient_name: "Rahul Kumar",
    blood_group: "B+",
    urgency_days: 12,
    current_step: "completed",
    status: "completed",
    steps: [
      { step_name: "Patient Registered", status: "completed", started_at: "10:00 AM", completed_at: "10:00 AM", details: "Age 12, Thalassemia Major" },
      { step_name: "Medical Report Scanned", status: "completed", started_at: "10:01 AM", completed_at: "10:02 AM", details: "Hb: 9.2, Ferritin: 45" },
      { step_name: "Urgency Calculated", status: "completed", started_at: "10:02 AM", completed_at: "10:02 AM", details: "12 days — SCHEDULED" },
      { step_name: "Blood Bank Search", status: "completed", started_at: "10:03 AM", completed_at: "10:04 AM", details: "NIMS: 4 units B+ found" },
      { step_name: "Blood Reserved", status: "completed", started_at: "10:04 AM", completed_at: "10:05 AM", details: "4 units reserved at NIMS" },
      { step_name: "Workflow Complete", status: "completed", started_at: "10:05 AM", completed_at: "10:05 AM", details: "No donor search needed" },
    ],
  },
];

const donorRankings = [
  { rank: 1, name: "Ravi Kumar", blood_group: "O+" as BloodGroup, score: 0.92, distance: 2.1, status: "confirmed" },
  { rank: 2, name: "Suresh M", blood_group: "O+" as BloodGroup, score: 0.88, distance: 3.4, status: "confirmed" },
  { rank: 3, name: "Priya Sharma", blood_group: "O+" as BloodGroup, score: 0.85, distance: 5.2, status: "calling" },
  { rank: 4, name: "Amit Reddy", blood_group: "O+" as BloodGroup, score: 0.82, distance: 6.1, status: "confirmed" },
  { rank: 5, name: "Deepa V", blood_group: "O+" as BloodGroup, score: 0.79, distance: 7.3, status: "declined" },
  { rank: 6, name: "Kiran P", blood_group: "O+" as BloodGroup, score: 0.76, distance: 8.0, status: "calling" },
  { rank: 7, name: "Lakshmi N", blood_group: "O+" as BloodGroup, score: 0.73, distance: 9.1, status: "pending" },
];

const insights = [
  {
    pattern: "O+ requests in Hyderabad fail 40% in Tier 1",
    action: "System now starts with Tier 2 for this combination",
    result: "Success rate improved 23%",
  },
  {
    pattern: "Donors respond 35% better to calls between 6-8 PM",
    action: "Campaign scheduler adjusted to evening hours",
    result: "Confirmation rate up from 42% to 57%",
  },
  {
    pattern: "B- blood group has lowest donor density (0.3/km)",
    action: "Expanded search radius from 10km to 25km for B-",
    result: "Match rate improved from 15% to 38%",
  },
  {
    pattern: "Mon-Sat donors more responsive than Sunday",
    action: "Sunday campaigns now use SMS-first approach",
    result: "Cost per confirmation reduced 45%",
  },
];

const activityFeed = [
  { time: "12:03 PM", event: "Voice campaign started for Kavya (O+)", type: "call" },
  { time: "12:02 PM", event: "Apollo Blood Bank: 2 units O+ reserved", type: "reserve" },
  { time: "12:01 PM", event: "Urgency calculated: Kavya — 3 days", type: "urgency" },
  { time: "11:33 AM", event: "Blood bank search started for Arjun (O-)", type: "search" },
  { time: "11:32 AM", event: "Urgency calculated: Arjun — 2 days CRITICAL", type: "urgency" },
  { time: "10:05 AM", event: "Workflow completed for Rahul (B+) — blood reserved", type: "complete" },
  { time: "10:02 AM", event: "Urgency calculated: Rahul — 12 days scheduled", type: "urgency" },
];

export default function CoordinatorPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("wf001");
  const active = workflows.find((w) => w.id === selectedWorkflow);

  const getUrgencyColor = (days: number) => {
    if (days <= 3) return "var(--blood)";
    if (days <= 7) return "var(--orange)";
    return "var(--green)";
  };

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold">Coordinator Command Center</h1>
      <p className="mb-8 text-[var(--text-secondary)]">
        Unified workflow timeline, donor rankings, and self-learning insights.
      </p>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: Active Workflows */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold">Active Workflows</h2>
          {workflows.map((wf) => (
            <button
              key={wf.id}
              onClick={() => setSelectedWorkflow(wf.id)}
              className={`w-full rounded-2xl border p-5 text-left transition-all ${
                selectedWorkflow === wf.id
                  ? "border-blood bg-blood/5"
                  : "border-border bg-card hover:bg-card-hover"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span
                    className="rounded-lg px-2 py-0.5 text-xs font-bold"
                    style={{
                      background: `${BLOOD_GROUP_COLORS[wf.blood_group]}20`,
                      color: BLOOD_GROUP_COLORS[wf.blood_group],
                    }}
                  >
                    {wf.blood_group}
                  </span>
                  <span className="font-semibold">{wf.patient_name}</span>
                </div>
                <span
                  className="font-mono text-lg font-bold"
                  style={{ color: getUrgencyColor(wf.urgency_days) }}
                >
                  {wf.urgency_days}d
                </span>
              </div>
              <p className="mt-2 text-xs text-[var(--text-muted)]">
                Step: {wf.current_step.replace(/_/g, " ")} &middot;{" "}
                {wf.status === "completed" ? "Done" : "In Progress"}
              </p>
            </button>
          ))}

          {/* Activity Feed */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <h3 className="mb-3 text-sm font-bold text-[var(--text-secondary)]">Activity Feed</h3>
            <div className="space-y-2">
              {activityFeed.map((item, i) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  <span className="mt-0.5 shrink-0 text-[var(--text-muted)]">{item.time}</span>
                  <span className="text-[var(--text-secondary)]">{item.event}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center: Workflow Timeline */}
        <div>
          <h2 className="mb-4 text-lg font-bold">
            Workflow: {active?.patient_name}
          </h2>
          <div className="rounded-2xl border border-border bg-card p-6">
            {active?.steps.map((step, i) => {
              const isLast = i === active.steps.length - 1;
              return (
                <div key={i} className="flex gap-4">
                  {/* Timeline line */}
                  <div className="flex flex-col items-center">
                    <div
                      className={`h-4 w-4 rounded-full border-2 ${
                        step.status === "completed"
                          ? "border-success bg-success"
                          : step.status === "active"
                          ? "border-info bg-info animate-pulse-blue"
                          : "border-border bg-surface"
                      }`}
                    />
                    {!isLast && (
                      <div
                        className={`w-0.5 flex-1 ${
                          step.status === "completed" ? "bg-success" : "bg-border"
                        }`}
                      />
                    )}
                  </div>

                  {/* Step content */}
                  <div className={`pb-6 ${isLast ? "" : ""}`}>
                    <p
                      className={`text-sm font-semibold ${
                        step.status === "active"
                          ? "text-info"
                          : step.status === "completed"
                          ? "text-[var(--text-primary)]"
                          : "text-[var(--text-muted)]"
                      }`}
                    >
                      {step.step_name}
                    </p>
                    {step.details && (
                      <p className="mt-1 text-xs text-[var(--text-secondary)]">
                        {step.details}
                      </p>
                    )}
                    {step.started_at && (
                      <p className="mt-1 text-xs text-[var(--text-muted)]">
                        {step.started_at}
                        {step.completed_at && ` → ${step.completed_at}`}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Donor Rankings + Insights */}
        <div className="space-y-6">
          {/* Donor Rankings */}
          <div className="rounded-2xl border border-border bg-card p-5">
            <h3 className="mb-4 text-sm font-bold text-[var(--text-secondary)]">
              Donor Rankings (O+ Hyderabad)
            </h3>
            <div className="space-y-2">
              {donorRankings.map((d) => (
                <div
                  key={d.rank}
                  className="flex items-center justify-between rounded-xl bg-surface p-3"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                        d.rank === 1
                          ? "bg-yellow-500/20 text-yellow-400"
                          : d.rank === 2
                          ? "bg-gray-400/20 text-gray-300"
                          : d.rank === 3
                          ? "bg-amber-600/20 text-amber-500"
                          : "bg-surface text-[var(--text-muted)]"
                      }`}
                    >
                      #{d.rank}
                    </span>
                    <div>
                      <p className="text-sm font-semibold">{d.name}</p>
                      <p className="text-xs text-[var(--text-muted)]">
                        {d.distance}km &middot; {(d.score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                      d.status === "confirmed"
                        ? "bg-success/20 text-success"
                        : d.status === "declined"
                        ? "bg-[var(--highlight)]/20 text-[var(--highlight)]"
                        : d.status === "calling"
                        ? "bg-info/20 text-info"
                        : "bg-surface text-[var(--text-muted)]"
                    }`}
                  >
                    {d.status}
                  </span>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-[var(--text-muted)]">
              Score = Eligibility x Reliability x Proximity x Willingness x Availability
            </p>
          </div>

          {/* Self-Learning Insights */}
          <div className="rounded-2xl border-l-4 border-[var(--ai)] bg-card p-5">
            <h3 className="mb-4 text-sm font-bold text-[var(--ai)]">
              Self-Learning Insights
            </h3>
            <div className="space-y-3">
              {insights.map((insight, i) => (
                <div key={i} className="rounded-xl bg-surface p-3">
                  <p className="text-xs font-semibold text-[var(--text-primary)]">
                    {insight.pattern}
                  </p>
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {insight.action}
                  </p>
                  <p className="mt-1 text-xs text-success">{insight.result}</p>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-[var(--text-muted)]">
              Powered by SageMaker retraining + CloudWatch failure logs
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
