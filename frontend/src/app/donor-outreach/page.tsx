"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { CallResponse, BloodGroup } from "@/lib/types";
import { BLOOD_GROUP_COLORS } from "@/lib/types";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import { ProgressBar } from "@/components/ProgressBar";
import { Phone } from "@phosphor-icons/react";

interface DonorCall {
  donor_id: string;
  name: string;
  blood_group: BloodGroup;
  distance_km: number;
  readiness_score: number;
  language: string;
  status: CallResponse["status"];
}

const mockDonors: DonorCall[] = [
  { donor_id: "d01", name: "Ravi Kumar", blood_group: "O+", distance_km: 2.1, readiness_score: 0.92, language: "Hindi", status: "pending" },
  { donor_id: "d02", name: "Suresh M", blood_group: "O+", distance_km: 3.4, readiness_score: 0.88, language: "Telugu", status: "pending" },
  { donor_id: "d03", name: "Priya Sharma", blood_group: "O+", distance_km: 5.2, readiness_score: 0.85, language: "Hindi", status: "pending" },
  { donor_id: "d04", name: "Amit Reddy", blood_group: "O+", distance_km: 6.1, readiness_score: 0.82, language: "Telugu", status: "pending" },
  { donor_id: "d05", name: "Deepa V", blood_group: "O+", distance_km: 7.3, readiness_score: 0.79, language: "Hindi", status: "pending" },
  { donor_id: "d06", name: "Kiran P", blood_group: "O+", distance_km: 8.0, readiness_score: 0.76, language: "Telugu", status: "pending" },
  { donor_id: "d07", name: "Lakshmi N", blood_group: "O+", distance_km: 9.1, readiness_score: 0.73, language: "Tamil", status: "pending" },
  { donor_id: "d08", name: "Manoj S", blood_group: "O+", distance_km: 10.2, readiness_score: 0.71, language: "Hindi", status: "pending" },
  { donor_id: "d09", name: "Neha G", blood_group: "O+", distance_km: 11.0, readiness_score: 0.68, language: "Telugu", status: "pending" },
  { donor_id: "d10", name: "Omar F", blood_group: "O+", distance_km: 12.3, readiness_score: 0.65, language: "Hindi", status: "pending" },
  { donor_id: "d11", name: "Padma R", blood_group: "O+", distance_km: 13.1, readiness_score: 0.63, language: "Telugu", status: "pending" },
  { donor_id: "d12", name: "Raj T", blood_group: "O+", distance_km: 14.5, readiness_score: 0.60, language: "Tamil", status: "pending" },
  { donor_id: "d13", name: "Sita K", blood_group: "O+", distance_km: 15.2, readiness_score: 0.58, language: "Hindi", status: "pending" },
  { donor_id: "d14", name: "Tariq A", blood_group: "O+", distance_km: 16.0, readiness_score: 0.55, language: "Hindi", status: "pending" },
  { donor_id: "d15", name: "Uma D", blood_group: "O+", distance_km: 17.3, readiness_score: 0.52, language: "Telugu", status: "pending" },
  { donor_id: "d16", name: "Vikram J", blood_group: "O+", distance_km: 18.1, readiness_score: 0.50, language: "Hindi", status: "pending" },
  { donor_id: "d17", name: "Waseem K", blood_group: "O+", distance_km: 19.0, readiness_score: 0.48, language: "Hindi", status: "pending" },
  { donor_id: "d18", name: "Xena L", blood_group: "O+", distance_km: 20.2, readiness_score: 0.45, language: "Telugu", status: "pending" },
  { donor_id: "d19", name: "Yash B", blood_group: "O+", distance_km: 21.5, readiness_score: 0.42, language: "Marathi", status: "pending" },
  { donor_id: "d20", name: "Zara M", blood_group: "O+", distance_km: 22.0, readiness_score: 0.40, language: "Hindi", status: "pending" },
];

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  pending:    { color: "var(--text-muted)", label: "Waiting" },
  calling:    { color: "var(--info)", label: "Calling" },
  connected:  { color: "var(--positive)", label: "Connected" },
  confirmed:  { color: "var(--success)", label: "Confirmed" },
  declined:   { color: "var(--highlight)", label: "Declined" },
  no_answer:  { color: "var(--warning)", label: "No Answer" },
};

export default function DonorOutreachPage() {
  const [donors, setDonors] = useState<DonorCall[]>(mockDonors);
  const [campaignActive, setCampaignActive] = useState(false);
  const [targetCount] = useState(5);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const confirmedCount = donors.filter((d) => d.status === "confirmed").length;
  const declinedCount = donors.filter((d) => d.status === "declined").length;
  const callingCount = donors.filter((d) => d.status === "calling" || d.status === "connected").length;

  const simulateCall = useCallback(() => {
    setDonors((prev) => {
      const confirmed = prev.filter((d) => d.status === "confirmed").length;
      if (confirmed >= targetCount) {
        return prev.map((d) =>
          d.status === "calling" || d.status === "connected" || d.status === "pending"
            ? { ...d, status: "pending" as const }
            : d
        );
      }

      const updated = [...prev];
      const callingIdx = updated.findIndex((d) => d.status === "calling");
      if (callingIdx !== -1) {
        const rand = Math.random();
        if (rand < 0.45) {
          updated[callingIdx] = { ...updated[callingIdx], status: "confirmed" };
        } else if (rand < 0.7) {
          updated[callingIdx] = { ...updated[callingIdx], status: "declined" };
        } else {
          updated[callingIdx] = { ...updated[callingIdx], status: "no_answer" };
        }
      }

      const nextPending = updated.findIndex((d) => d.status === "pending");
      if (nextPending !== -1) {
        updated[nextPending] = { ...updated[nextPending], status: "calling" };
      }

      const stillCalling = updated.filter((d) => d.status === "calling").length;
      if (stillCalling === 0) return updated;

      const connectedIdx = updated.findIndex((d) => d.status === "calling");
      if (connectedIdx !== -1 && Math.random() > 0.5) {
        updated[connectedIdx] = { ...updated[connectedIdx], status: "connected" };
      }

      return updated;
    });
  }, [targetCount]);

  useEffect(() => {
    if (campaignActive) {
      setDonors((prev) =>
        prev.map((d, i) => (i < 5 ? { ...d, status: "calling" as const } : d))
      );
      timerRef.current = setInterval(simulateCall, 1500);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [campaignActive, simulateCall]);

  useEffect(() => {
    if (confirmedCount >= targetCount && campaignActive) {
      if (timerRef.current) clearInterval(timerRef.current);
      setCampaignActive(false);
      setDonors((prev) =>
        prev.map((d) =>
          d.status === "calling" || d.status === "connected"
            ? { ...d, status: "pending" as const }
            : d
        )
      );
    }
  }, [confirmedCount, targetCount, campaignActive]);

  const handleCancel = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setCampaignActive(false);
    setDonors((prev) =>
      prev.map((d) =>
        d.status === "calling" || d.status === "connected"
          ? { ...d, status: "pending" as const }
          : d
      )
    );
  };

  const handleReset = () => {
    setDonors(mockDonors);
    setCampaignActive(false);
  };

  const progressPct = (confirmedCount / targetCount) * 100;

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">AI Voice Call Campaign</h1>
      <p className="mb-8 text-secondary">
        Parallel outbound calls to 20 donors. AI speaks in donor&apos;s language via Amazon Polly + Lex.
      </p>

      {/* Campaign Info */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Patient:</span>
            <span className="font-semibold font-display">Kavya Reddy</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Blood Group:</span>
            <Badge type="blood" value="O+" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Units Needed:</span>
            <span className="font-semibold font-mono">2</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Urgency:</span>
            <Badge type="status" value="urgent" />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">AWS:</span>
            <span className="rounded-lg bg-ai/15 px-2 py-0.5 text-xs text-ai">Connect + Polly + Lex</span>
          </div>
        </div>
      </Card>

      {/* Progress */}
      <Card className="mb-6">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex gap-6">
            <div>
              <p
                className="text-3xl font-bold font-mono"
                style={{ color: confirmedCount >= targetCount ? "var(--success)" : "var(--blood)" }}
              >
                {confirmedCount}/{targetCount}
              </p>
              <p className="text-sm text-muted">Confirmed</p>
            </div>
            <div>
              <p className="text-2xl font-bold font-mono text-info">{callingCount}</p>
              <p className="text-sm text-muted">Active Calls</p>
            </div>
            <div>
              <p className="text-2xl font-bold font-mono text-highlight">{declinedCount}</p>
              <p className="text-sm text-muted">Declined</p>
            </div>
          </div>

          <div className="flex gap-3">
            {!campaignActive && confirmedCount === 0 && (
              <button
                onClick={() => setCampaignActive(true)}
                className="rounded-lg bg-blood px-8 py-3 font-semibold font-display text-white transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:brightness-110 hover:-translate-y-[1px] active:scale-[0.98]"
              >
                Start All Calls
              </button>
            )}
            {campaignActive && (
              <button
                onClick={handleCancel}
                className="rounded-lg border border-highlight px-6 py-3 text-sm font-semibold font-display text-highlight hover:bg-highlight/10 transition-colors"
              >
                Cancel Remaining
              </button>
            )}
            {confirmedCount >= targetCount && (
              <button
                onClick={handleReset}
                className="rounded-lg border border-border px-6 py-3 text-sm font-semibold font-display text-secondary hover:bg-card-hover transition-colors"
              >
                Reset Campaign
              </button>
            )}
          </div>
        </div>

        <ProgressBar
          value={confirmedCount}
          max={targetCount}
          label={
            confirmedCount >= targetCount
              ? `Target met! ${confirmedCount} donors confirmed. Remaining calls auto-cancelled.`
              : `${confirmedCount} of ${targetCount} donors confirmed`
          }
        />
      </Card>

      {/* Call Script Preview */}
      <Card className="mb-6">
        <h3 className="mb-3 text-sm font-bold font-display text-ai">Call Script (Amazon Polly)</h3>
        <div className="rounded-lg bg-surface p-4 text-sm text-secondary">
          <p>&quot;Namaste, this is an automated call from <span className="font-semibold text-warning">Blood Warriors</span>.</p>
          <p className="mt-1">A patient with <span className="font-semibold text-blood">O Positive</span> blood group needs your help this week.</p>
          <p className="mt-1">Can you donate? Please press <span className="font-semibold text-success">1 for yes</span> or <span className="font-semibold text-highlight">2 for no</span>.&quot;</p>
        </div>
      </Card>

      {/* Donor Grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 md:grid-cols-5">
        {donors.map((donor) => {
          const config = STATUS_CONFIG[donor.status];
          const isActive = donor.status === "calling" || donor.status === "connected";
          return (
            <div
              key={donor.donor_id}
              className={`rounded-xl border p-4 transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                isActive ? "animate-pulse-border-blue" : ""
              } ${
                donor.status === "confirmed" ? "animate-pulse-border-teal" : ""
              }`}
              style={{
                borderColor: `${config.color}40`,
                background: donor.status === "pending" ? "var(--bg-card)" : `${config.color}08`,
              }}
            >
              <p className="text-sm font-semibold font-display">{donor.name}</p>
              <div className="mt-1 flex items-center gap-2">
                <Badge type="blood" value={donor.blood_group} />
                <span className="text-xs text-muted font-mono">
                  {donor.distance_km}km
                </span>
              </div>
              <p className="mt-1 text-xs text-muted font-mono">
                Score: {donor.readiness_score.toFixed(2)} · {donor.language}
              </p>
              <div className="mt-3 flex items-center gap-1.5">
                <div
                  className="h-2 w-2 rounded-full"
                  style={{ background: config.color }}
                />
                <span className="text-xs font-semibold font-display" style={{ color: config.color }}>
                  {config.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
