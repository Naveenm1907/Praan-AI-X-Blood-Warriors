"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import {
  Brain,
  MapPin,
  Phone,
  Clock,
  Trophy,
  CheckCircle,
  Star,
  Lightning,
} from "@phosphor-icons/react";
import type { BloodGroup } from "@/lib/types";

interface RankedDonor {
  donor_id: string;
  name: string;
  blood_group: BloodGroup;
  distance_km: number;
  readiness_score: number;
  calls_to_donations_ratio: number;
  last_donation_date: string;
  phone?: string;
  location?: string;
  language?: string;
  total_donations?: number;
  total_calls?: number;
  scoring_method?: string;
}

interface Patient {
  id: number;
  name: string;
  blood_group: string;
  location?: string;
  urgency_level?: string;
  days_until_transfusion?: number;
}

export default function DonorsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)]"></div>
        </div>
      }
    >
      <DonorsContent />
    </Suspense>
  );
}

function DonorsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const patientId = searchParams.get("patient_id");
  const bloodGroup = searchParams.get("blood_group");

  const [donors, setDonors] = useState<RankedDonor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scoringMethod, setScoringMethod] = useState<string>("");
  const [selectedDonors, setSelectedDonors] = useState<Set<string>>(new Set());
  const [patient, setPatient] = useState<Patient | null>(null);

  useEffect(() => {
    if (patientId) {
      fetchPatient();
    }
    if (bloodGroup) {
      fetchRankedDonors();
    } else {
      setLoading(false);
    }
  }, [bloodGroup, patientId]);

  async function fetchPatient() {
    try {
      const data = await api.get<Patient>(`/api/patient/patients/${patientId}`);
      setPatient(data);
    } catch (err) {
      console.error("Failed to fetch patient:", err);
    }
  }

  async function fetchRankedDonors() {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({
        blood_group: bloodGroup || "",
        count: "20",
      });
      if (patientId) {
        params.set("patient_id", patientId);
      }
      const data = await api.get<RankedDonor[]>(
        `/api/donor/rank?${params.toString()}`
      );
      setDonors(data);
      if (data.length > 0 && data[0].scoring_method) {
        setScoringMethod(data[0].scoring_method);
      }
    } catch (err) {
      console.error("Failed to rank donors:", err);
      setError("Failed to rank donors. Check backend connection.");
    } finally {
      setLoading(false);
    }
  }

  function toggleDonor(donorId: string) {
    setSelectedDonors((prev) => {
      const next = new Set(prev);
      if (next.has(donorId)) {
        next.delete(donorId);
      } else {
        next.add(donorId);
      }
      return next;
    });
  }

  function selectTop(n: number) {
    setSelectedDonors(new Set(donors.slice(0, n).map((d) => d.donor_id)));
  }

  function handleProceedToCampaign() {
    const ids = Array.from(selectedDonors).join(",");
    router.push(
      `/donor-outreach?patient_id=${patientId}&blood_group=${bloodGroup}&donor_ids=${ids}`
    );
  }

  function getScoreColor(score: number): string {
    if (score >= 0.8) return "var(--success)";
    if (score >= 0.6) return "var(--positive)";
    if (score >= 0.4) return "var(--warning)";
    return "var(--text-muted)";
  }

  function getScoreLabel(score: number): string {
    if (score >= 0.8) return "Excellent";
    if (score >= 0.6) return "Good";
    if (score >= 0.4) return "Fair";
    return "Low";
  }

  function getDaysSinceDonation(dateStr: string): number | null {
    if (!dateStr) return null;
    const last = new Date(dateStr);
    const now = new Date();
    return Math.floor((now.getTime() - last.getTime()) / (1000 * 60 * 60 * 24));
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">AI Donor Matching</h1>
      <p className="mb-8 text-secondary">
        XGBoost-powered donor ranking. Scored on eligibility × reliability × proximity × willingness × availability.
      </p>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)] mx-auto mb-4"></div>
            <p className="text-secondary">Running AI donor matching model...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-8 text-center">
          <Brain size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
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
          <Brain size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
          <p className="text-lg font-semibold text-warning mb-2">No blood group selected</p>
          <p className="text-secondary mb-4">Please register a patient first or select a blood group.</p>
          <Link
            href="/patient"
            className="rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Go to Patient Registration
          </Link>
        </div>
      )}

      {/* Main Content */}
      {!loading && !error && bloodGroup && (
        <>
          {/* Patient + Method Info Bar */}
          <Card className="mb-6">
            <div className="flex flex-wrap items-center gap-4">
              {patient ? (
                <>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted">Patient:</span>
                    <span className="font-semibold">{patient.name}</span>
                  </div>
                  {patient.location && (
                    <div className="flex items-center gap-2">
                      <MapPin size={16} weight="regular" className="text-muted" />
                      <span className="text-sm">{patient.location}</span>
                    </div>
                  )}
                  {patient.urgency_level && (
                    <div className="flex items-center gap-2">
                      <Clock size={16} weight="regular" className="text-muted" />
                      <span className="text-sm font-semibold" style={{ color: patient.urgency_level === 'CRITICAL' ? 'var(--blood)' : patient.urgency_level === 'URGENT' ? 'var(--warning)' : 'var(--info)' }}>
                        {patient.urgency_level}
                      </span>
                    </div>
                  )}
                  {patient.days_until_transfusion !== null && patient.days_until_transfusion !== undefined && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted">Days until transfusion:</span>
                      <span className="font-semibold font-mono">{patient.days_until_transfusion}</span>
                    </div>
                  )}
                </>
              ) : patientId ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted">Patient ID:</span>
                  <span className="font-semibold font-mono">{patientId}</span>
                </div>
              ) : null}
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted">Blood Group:</span>
                <Badge type="blood" value={bloodGroup} />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted">Donors Found:</span>
                <span className="font-semibold font-mono">{donors.length}</span>
              </div>
              {scoringMethod && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted">Model:</span>
                  <span className="rounded-lg bg-ai/15 px-2 py-0.5 text-xs text-ai">
                    {scoringMethod === "xgboost_ai" ? "XGBoost AI" : "Rule-Based"}
                  </span>
                </div>
              )}
            </div>
          </Card>

          {/* Summary Stats */}
          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Card className="text-center">
              <Trophy className="mx-auto mb-2" size={24} weight="regular" style={{ color: "var(--success)" }} />
              <p className="text-2xl font-bold font-mono" style={{ color: "var(--success)" }}>
                {donors.filter((d) => d.readiness_score >= 0.8).length}
              </p>
              <p className="text-xs text-muted">Excellent Matches</p>
            </Card>
            <Card className="text-center">
              <Star className="mx-auto mb-2" size={24} weight="regular" style={{ color: "var(--positive)" }} />
              <p className="text-2xl font-bold font-mono" style={{ color: "var(--positive)" }}>
                {donors.filter((d) => d.readiness_score >= 0.6 && d.readiness_score < 0.8).length}
              </p>
              <p className="text-xs text-muted">Good Matches</p>
            </Card>
            <Card className="text-center">
              <MapPin className="mx-auto mb-2" size={24} weight="regular" style={{ color: "var(--info)" }} />
              <p className="text-2xl font-bold font-mono" style={{ color: "var(--info)" }}>
                {donors.length > 0 ? donors[0].distance_km?.toFixed(1) : "—"}km
              </p>
              <p className="text-xs text-muted">Nearest Donor</p>
            </Card>
            <Card className="text-center">
              <Lightning className="mx-auto mb-2" size={24} weight="regular" style={{ color: "var(--blood)" }} />
              <p className="text-2xl font-bold font-mono" style={{ color: "var(--blood)" }}>
                {donors.length > 0 ? ((donors[0].readiness_score || 0) * 100).toFixed(0) : "—"}%
              </p>
              <p className="text-xs text-muted">Top Score</p>
            </Card>
          </div>

          {/* Selection Actions */}
          <div className="mb-6 flex flex-wrap items-center gap-3">
            <span className="text-sm font-semibold font-display text-secondary">
              Selected: {selectedDonors.size} donors
            </span>
            <button
              onClick={() => selectTop(5)}
              className="rounded-lg border border-border bg-card px-4 py-2 text-xs font-semibold font-display text-secondary hover:bg-card-hover transition-colors"
            >
              Select Top 5
            </button>
            <button
              onClick={() => selectTop(10)}
              className="rounded-lg border border-border bg-card px-4 py-2 text-xs font-semibold font-display text-secondary hover:bg-card-hover transition-colors"
            >
              Select Top 10
            </button>
            <button
              onClick={() => setSelectedDonors(new Set())}
              className="rounded-lg border border-border bg-card px-4 py-2 text-xs font-semibold font-display text-muted hover:bg-card-hover transition-colors"
            >
              Clear All
            </button>
            <div className="flex-1" />
            <button
              onClick={handleProceedToCampaign}
              disabled={selectedDonors.size === 0}
              className="rounded-lg bg-blood px-6 py-3 text-sm font-semibold font-display text-white hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Voice Campaign ({selectedDonors.size}) &rarr;
            </button>
          </div>

          {/* Donor Rankings Table */}
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-surface">
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Donor
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Score
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Distance
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Last Donation
                    </th>
                    <th className="py-3 px-4 text-left text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Conversion
                    </th>
                    <th className="py-3 px-4 text-center text-xs font-semibold font-display text-muted uppercase tracking-wider">
                      Select
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {donors.map((donor, i) => {
                    const daysSince = getDaysSinceDonation(donor.last_donation_date);
                    const isEligible = daysSince === null || daysSince >= 120;
                    const isSelected = selectedDonors.has(donor.donor_id);

                    return (
                      <tr
                        key={donor.donor_id}
                        className={`border-b border-border transition-colors ${
                          isSelected
                            ? "bg-blood/5"
                            : "hover:bg-card-hover"
                        }`}
                      >
                        {/* Rank */}
                        <td className="py-3 px-4">
                          <span
                            className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold font-mono ${
                              i === 0
                                ? "bg-yellow-500/20 text-yellow-400"
                                : i === 1
                                ? "bg-gray-400/20 text-gray-300"
                                : i === 2
                                ? "bg-amber-600/20 text-amber-500"
                                : "bg-surface text-muted"
                            }`}
                          >
                            #{i + 1}
                          </span>
                        </td>

                        {/* Donor Info */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-3">
                            <div>
                              <p className="text-sm font-semibold font-display">{donor.name}</p>
                              <div className="mt-0.5 flex items-center gap-2">
                                <Badge type="blood" value={donor.blood_group} />
                                {donor.language && (
                                  <span className="text-xs text-muted">{donor.language}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </td>

                        {/* Score */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div
                              className="h-2 w-16 overflow-hidden rounded-full bg-surface"
                            >
                              <div
                                className="h-full rounded-full transition-all"
                                style={{
                                  width: `${(donor.readiness_score || 0) * 100}%`,
                                  background: getScoreColor(donor.readiness_score),
                                }}
                              />
                            </div>
                            <div>
                              <p className="text-sm font-bold font-mono" style={{ color: getScoreColor(donor.readiness_score) }}>
                                {((donor.readiness_score || 0) * 100).toFixed(0)}%
                              </p>
                              <p className="text-[10px] text-muted">{getScoreLabel(donor.readiness_score)}</p>
                            </div>
                          </div>
                        </td>

                        {/* Distance */}
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1">
                            <MapPin size={14} weight="regular" className="text-muted" />
                            <span className="text-sm font-mono">
                              {donor.distance_km?.toFixed(1)}km
                            </span>
                          </div>
                        </td>

                        {/* Last Donation */}
                        <td className="py-3 px-4">
                          {daysSince !== null ? (
                            <div className="flex items-center gap-1">
                              <Clock size={14} weight="regular" className="text-muted" />
                              <span className={`text-sm font-mono ${isEligible ? "" : "text-warning"}`}>
                                {daysSince}d ago
                              </span>
                              {!isEligible && (
                                <span className="rounded bg-warning/20 px-1.5 py-0.5 text-[10px] font-mono text-warning">
                                  Not eligible
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-muted">Never</span>
                          )}
                        </td>

                        {/* Conversion */}
                        <td className="py-3 px-4">
                          <span className="text-sm font-mono">
                            {((donor.calls_to_donations_ratio || 0) * 100).toFixed(0)}%
                          </span>
                          {donor.total_donations !== undefined && (
                            <p className="text-[10px] text-muted">
                              {donor.total_donations} donations / {donor.total_calls || 0} calls
                            </p>
                          )}
                        </td>

                        {/* Select */}
                        <td className="py-3 px-4 text-center">
                          <button
                            onClick={() => toggleDonor(donor.donor_id)}
                            className={`flex h-8 w-8 items-center justify-center rounded-lg mx-auto transition-all ${
                              isSelected
                                ? "bg-blood text-white"
                                : "border border-border bg-surface hover:bg-card-hover"
                            }`}
                          >
                            {isSelected ? (
                              <CheckCircle size={18} weight="fill" />
                            ) : (
                              <span className="text-xs text-muted">+</span>
                            )}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Scoring Methodology */}
          <Card className="mt-6">
            <h3 className="mb-3 text-sm font-bold font-display text-secondary">
              Scoring Methodology
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
              {[
                { label: "Eligibility", weight: "25%", desc: "Days since last donation ≥ 120" },
                { label: "Reliability", weight: "30%", desc: "Call-to-donation conversion rate" },
                { label: "Proximity", weight: "25%", desc: "Distance from patient location" },
                { label: "Willingness", weight: "20%", desc: "Total historical donations" },
                { label: "Availability", weight: "Bonus", desc: "Active status + recent contact" },
              ].map((factor) => (
                <div key={factor.label} className="rounded-lg bg-surface p-3">
                  <p className="text-xs font-semibold font-display text-primary">{factor.label}</p>
                  <p className="text-xs font-mono text-blood">{factor.weight}</p>
                  <p className="mt-1 text-[10px] text-muted">{factor.desc}</p>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
