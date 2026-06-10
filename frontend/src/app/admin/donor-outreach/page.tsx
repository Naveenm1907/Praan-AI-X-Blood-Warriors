"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import type { CallResponse, BloodGroup } from "@/lib/types";
import { BLOOD_GROUP_COLORS } from "@/lib/types";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import { ProgressBar } from "@/components/ProgressBar";
import { Phone } from "@phosphor-icons/react";
import { api } from "@/lib/api";

interface DonorCall {
  donor_id: string;
  name: string;
  blood_group: BloodGroup;
  distance_km: number;
  readiness_score: number;
  language: string;
  phone?: string;
  status: CallResponse["status"];
}

interface Campaign {
  campaign_id: string;
  patient_id: string;
  donor_ids: string[];
  status: string;
  responses: Record<string, CallResponse>;
  language: string;
  target_count: number;
  confirmed_count: number;
  started_at: string;
}

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  pending:    { color: "var(--text-muted)", label: "Waiting" },
  calling:    { color: "var(--info)", label: "Calling" },
  connected:  { color: "var(--positive)", label: "Connected" },
  confirmed:  { color: "var(--success)", label: "Confirmed" },
  declined:   { color: "var(--highlight)", label: "Declined" },
  no_answer:  { color: "var(--warning)", label: "No Answer" },
};

export default function DonorOutreachPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)]"></div>
      </div>
    }>
      <DonorOutreachContent />
    </Suspense>
  );
}

function DonorOutreachContent() {
  const searchParams = useSearchParams();
  const patientId = searchParams.get("patient_id");
  const bloodGroup = searchParams.get("blood_group");

  const [donors, setDonors] = useState<DonorCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [campaignActive, setCampaignActive] = useState(false);
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [targetCount] = useState(5);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const confirmedCount = donors.filter((d) => d.status === "confirmed").length;
  const declinedCount = donors.filter((d) => d.status === "declined").length;
  const callingCount = donors.filter((d) => d.status === "calling" || d.status === "connected").length;

  useEffect(() => {
    if (bloodGroup) {
      fetchRankedDonors();
    } else {
      setLoading(false);
    }
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [bloodGroup]);

  async function fetchRankedDonors() {
    try {
      setLoading(true);
      setError(null);
      const ranked = await api.get<DonorCall[]>(
        `/api/donor/rank?blood_group=${bloodGroup}&count=20`
      );
      setDonors(ranked.map(d => ({ ...d, status: "pending" as const })));
    } catch (err) {
      console.error("Failed to fetch donors:", err);
      setError("Failed to load ranked donors. Check backend connection.");
    } finally {
      setLoading(false);
    }
  }

  async function startCampaign() {
    if (!patientId) {
      setError("No patient_id provided. Please start from patient registration page.");
      return;
    }

    try {
      setCampaignActive(true);
      const donorIds = donors.slice(0, 20).map(d => d.donor_id);

      const newCampaign = await api.post<Campaign>("/api/voice/campaign", {
        patient_id: patientId,
        donor_ids: donorIds,
        language: "en-IN",
        target_count: targetCount,
      });

      setCampaign(newCampaign);

      // Update donor statuses to "calling" for first 5
      setDonors(prev => prev.map((d, i) => ({
        ...d,
        status: i < 5 ? "calling" as const : d.status,
      })));

      // Start polling for campaign status
      pollCampaignStatus(newCampaign.campaign_id);
    } catch (err) {
      console.error("Failed to start campaign:", err);
      setError("Failed to start voice campaign.");
      setCampaignActive(false);
    }
  }

  function pollCampaignStatus(campaignId: string) {
    pollTimerRef.current = setInterval(async () => {
      try {
        const updatedCampaign = await api.get<Campaign>(`/api/voice/campaign/${campaignId}`);
        setCampaign(updatedCampaign);

        // Update donor statuses from campaign responses
        setDonors(prev => prev.map(d => {
          const response = updatedCampaign.responses[d.donor_id];
          if (response) {
            return { ...d, status: response.status as CallResponse["status"] };
          }
          return d;
        }));

        // Stop polling if campaign completed or cancelled
        if (updatedCampaign.status === "completed" || updatedCampaign.status === "cancelled") {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
          setCampaignActive(false);
        }
      } catch (err) {
        console.error("Polling failed:", err);
      }
    }, 2000);
  }

  async function handleCancel() {
    if (!campaign) return;

    try {
      await api.post("/api/voice/cancel", {
        campaign_id: campaign.campaign_id,
      });

      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      setCampaignActive(false);
      setDonors(prev => prev.map(d =>
        d.status === "calling" || d.status === "connected"
          ? { ...d, status: "pending" as const }
          : d
      ));
    } catch (err) {
      console.error("Failed to cancel campaign:", err);
    }
  }

  function handleReset() {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    setCampaign(null);
    setCampaignActive(false);
    setDonors(prev => prev.map(d => ({ ...d, status: "pending" as const })));
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">AI Voice Call Campaign</h1>
      <p className="mb-8 text-secondary">
        Parallel outbound calls to 20 donors. AI speaks in donor&apos;s language via Amazon Polly + Lex.
      </p>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)] mx-auto mb-4"></div>
            <p className="text-secondary">Loading ranked donors...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-8 text-center">
          <Phone size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
          <p className="text-lg font-semibold text-warning mb-2">{error}</p>
          <button
            onClick={fetchRankedDonors}
            className="mt-4 rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Retry
          </button>
        </div>
      )}

      {/* No blood group selected */}
      {!loading && !bloodGroup && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-8 text-center">
          <Phone size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
          <p className="text-lg font-semibold text-warning mb-2">No blood group selected</p>
          <p className="text-secondary mb-4">Please go through donor matching first.</p>
          <Link
            href="/donors"
            className="rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Go to Donor Matching
          </Link>
        </div>
      )}

      {/* Main Content */}
      {!loading && !error && bloodGroup && (
        <>
      {/* Campaign Info */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Patient ID:</span>
            <span className="font-semibold font-mono">{patientId || "Not specified"}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Blood Group:</span>
            {bloodGroup && <Badge type="blood" value={bloodGroup} />}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted">Target:</span>
            <span className="font-semibold font-mono">{targetCount} donors</span>
          </div>
          {campaign && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted">Campaign:</span>
              <span className="font-mono text-xs">{campaign.campaign_id}</span>
            </div>
          )}
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
                onClick={startCampaign}
                disabled={!patientId}
                className="rounded-lg bg-blood px-8 py-3 font-semibold font-display text-white transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:brightness-110 hover:-translate-y-[1px] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {patientId ? "Start All Calls" : "Need patient_id"}
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
            {campaign && (campaign.status === "completed" || campaign.status === "cancelled") && (
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
        </>
      )}
    </div>
  );
}
