"use client";

import { useState, useCallback } from "react";
import type { BloodGroup, Patient } from "@/lib/types";
import { BLOOD_GROUPS, BLOOD_GROUP_COLORS } from "@/lib/types";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Upload } from "@phosphor-icons/react";

interface OCRResult {
  hb: number;
  mcv: number;
  ferritin: number;
  mch: number;
}

export default function PatientPage() {
  const [patients, setPatients] = useState<Patient[]>([
    {
      patient_id: "p001", name: "Kavya Reddy", age: 8, blood_group: "O+",
      location: "Hyderabad", latitude: 17.385, longitude: 78.4867,
      last_transfusion_date: "2026-05-18", cycle_length_days: 21,
      hb_level: 6.8, ferritin_level: 12, mcv_level: 62,
      urgency_window_days: 3, created_at: "2026-06-01",
    },
    {
      patient_id: "p002", name: "Rahul Kumar", age: 12, blood_group: "B+",
      location: "Warangal", latitude: 17.9689, longitude: 79.5941,
      last_transfusion_date: "2026-05-10", cycle_length_days: 28,
      hb_level: 9.2, ferritin_level: 45, mcv_level: 78,
      urgency_window_days: 12, created_at: "2026-05-28",
    },
    {
      patient_id: "p003", name: "Arjun S", age: 10, blood_group: "O-",
      location: "Secunderabad", latitude: 17.4399, longitude: 78.4983,
      last_transfusion_date: "2026-05-28", cycle_length_days: 14,
      hb_level: 5.9, ferritin_level: 8, mcv_level: 55,
      urgency_window_days: 2, created_at: "2026-06-03",
    },
  ]);

  const [form, setForm] = useState({
    name: "", age: "", blood_group: "O+" as BloodGroup,
    location: "", last_transfusion_date: "", cycle_length_days: "",
  });
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null);
  const [uploading, setUploading] = useState(false);
  const [newPatient, setNewPatient] = useState<Patient | null>(null);

  const handleUpload = useCallback(() => {
    setUploading(true);
    setTimeout(() => {
      setOcrResult({
        hb: parseFloat((5 + Math.random() * 5).toFixed(1)),
        mcv: Math.floor(55 + Math.random() * 30),
        ferritin: Math.floor(5 + Math.random() * 50),
        mch: parseFloat((18 + Math.random() * 12).toFixed(1)),
      });
      setUploading(false);
    }, 2000);
  }, []);

  const calculateUrgency = useCallback((
    lastDate: string, cycleDays: number, hb: number
  ): number => {
    const last = new Date(lastDate);
    const next = new Date(last.getTime() + cycleDays * 24 * 60 * 60 * 1000);
    const today = new Date("2026-06-06");
    let days = Math.ceil((next.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    if (hb < 7) days = Math.max(days - 3, 1);
    if (hb < 5) days = 1;
    return Math.max(days, 1);
  }, []);

  const handleSubmit = () => {
    if (!form.name || !form.age || !form.last_transfusion_date || !ocrResult) return;
    const urgency = calculateUrgency(
      form.last_transfusion_date, parseInt(form.cycle_length_days) || 21, ocrResult.hb
    );
    const patient: Patient = {
      patient_id: `p${Date.now()}`,
      name: form.name,
      age: parseInt(form.age),
      blood_group: form.blood_group,
      location: form.location || "Hyderabad",
      latitude: 17.385,
      longitude: 78.4867,
      last_transfusion_date: form.last_transfusion_date,
      cycle_length_days: parseInt(form.cycle_length_days) || 21,
      hb_level: ocrResult.hb,
      ferritin_level: ocrResult.ferritin,
      mcv_level: ocrResult.mcv,
      urgency_window_days: urgency,
      created_at: "2026-06-06",
    };
    setNewPatient(patient);
    setPatients((prev) => [...prev, patient]);
  };

  const getUrgencyColor = (days: number) => {
    if (days <= 3) return "var(--blood)";
    if (days <= 7) return "var(--warning)";
    return "var(--positive)";
  };

  const getUrgencyLabel = (days: number) => {
    if (days <= 3) return "URGENT";
    if (days <= 7) return "MODERATE";
    return "SCHEDULED";
  };

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">Patient Onboarding</h1>
      <p className="mb-8 text-secondary">
        Register patient, upload medical report, and calculate transfusion urgency window.
      </p>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Form */}
        <Card>
          <h2 className="mb-6 text-xl font-bold font-display">Patient Registration</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                  placeholder="Patient name"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Age</label>
                <input
                  type="number"
                  value={form.age}
                  onChange={(e) => setForm({ ...form, age: e.target.value })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                  placeholder="Age"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Blood Group</label>
                <select
                  value={form.blood_group}
                  onChange={(e) => setForm({ ...form, blood_group: e.target.value as BloodGroup })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                >
                  {BLOOD_GROUPS.map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Location</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                  placeholder="City/District"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Last Transfusion</label>
                <input
                  type="date"
                  value={form.last_transfusion_date}
                  onChange={(e) => setForm({ ...form, last_transfusion_date: e.target.value })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-secondary">Cycle Length (days)</label>
                <input
                  type="number"
                  value={form.cycle_length_days}
                  onChange={(e) => setForm({ ...form, cycle_length_days: e.target.value })}
                  className="w-full rounded-lg border border-border bg-surface px-4 py-3 text-sm text-primary focus:border-[var(--border-focus)] focus:ring-2 focus:ring-[var(--border-focus)]/20 focus:outline-none"
                  placeholder="21"
                />
              </div>
            </div>

            {/* Medical Report Upload */}
            <div>
              <label className="mb-1 block text-sm font-medium text-secondary">Medical Report</label>
              <div
                onClick={handleUpload}
                className="cursor-pointer rounded-lg border-2 border-dashed border-border bg-surface p-8 text-center transition-all hover:border-blood"
              >
                {uploading ? (
                  <div>
                    <p className="text-sm text-ai">Textract scanning report...</p>
                    <p className="mt-1 text-xs text-muted">Extracting Hb, MCV, MCH, Ferritin</p>
                  </div>
                ) : ocrResult ? (
                  <p className="text-sm text-success">Report scanned successfully</p>
                ) : (
                  <div>
                    <Upload className="mx-auto" size={32} weight="regular" />
                    <p className="mt-2 text-sm text-secondary">
                      Click to upload PDF/Image (simulated Textract OCR)
                    </p>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={!form.name || !form.age || !form.last_transfusion_date || !ocrResult}
              className="w-full rounded-lg bg-blood py-3 text-sm font-semibold font-display text-white transition-all hover:brightness-110 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Register Patient & Calculate Urgency
            </button>
          </div>
        </Card>

        {/* Right side: OCR Results + Urgency */}
        <div className="space-y-6">
          {/* OCR Results */}
          {ocrResult && (
            <Card>
              <h2 className="mb-4 text-xl font-bold font-display">Medical Report Values</h2>
              <p className="mb-4 text-xs text-ai">Extracted by AWS Textract OCR</p>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { label: "Hb", value: `${ocrResult.hb} g/dL`, low: ocrResult.hb < 10 },
                  { label: "MCV", value: `${ocrResult.mcv} fL`, low: ocrResult.mcv < 80 },
                  { label: "Ferritin", value: `${ocrResult.ferritin} ng/mL`, low: ocrResult.ferritin < 30 },
                  { label: "MCH", value: `${ocrResult.mch} pg`, low: ocrResult.mch < 27 },
                ].map((item) => (
                  <div
                    key={item.label}
                    className={`rounded-lg border p-4 text-center ${
                      item.low ? "border-blood/30 bg-blood/5" : "border-border bg-surface"
                    }`}
                  >
                    <p className="text-xs text-muted">{item.label}</p>
                    <p className="mt-1 text-xl font-bold font-mono">{item.value}</p>
                    {item.low && (
                      <span className="text-xs text-blood">Low</span>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Urgency Window - top border instead of side-stripe */}
          {newPatient && newPatient.urgency_window_days && (
            <Card
              className="border-t-4"
              style={{ borderTopColor: getUrgencyColor(newPatient.urgency_window_days) }}
            >
              <h2 className="mb-2 text-xl font-bold font-display">Transfusion Urgency Window</h2>
              <div className="mt-4 text-center">
                <p
                  className="text-4xl font-bold font-mono"
                  style={{ color: getUrgencyColor(newPatient.urgency_window_days) }}
                >
                  {newPatient.urgency_window_days} DAYS
                </p>
                <p className="mt-2 text-sm text-secondary">
                  until next transfusion needed
                </p>
              </div>
              <div className="mt-6 flex items-center justify-center">
                <Badge
                  type="status"
                  value={getUrgencyLabel(newPatient.urgency_window_days).toLowerCase()}
                />
                <span className="ml-2 text-sm text-secondary">
                  Donor search starts NOW
                </span>
              </div>
              <div className="mt-6 flex gap-3">
                <Link href="/blood-bank">
                  <Button variant="secondary" size="sm" className="w-full">
                    Check Blood Banks
                  </Button>
                </Link>
                <Link href="/donor-outreach">
                  <Button variant="primary" size="sm" className="w-full">
                    Start Voice Calls
                  </Button>
                </Link>
              </div>
            </Card>
          )}

          {/* Existing Patients */}
          <Card>
            <h2 className="mb-4 text-xl font-bold font-display">Active Patients</h2>
            <div className="space-y-3">
              {patients
                .sort((a, b) => (a.urgency_window_days || 99) - (b.urgency_window_days || 99))
                .map((p) => (
                  <div
                    key={p.patient_id}
                    className="flex items-center justify-between rounded-lg border border-border bg-surface p-4"
                  >
                    <div className="flex items-center gap-3">
                      <Badge type="blood" value={p.blood_group} />
                      <div>
                        <p className="text-sm font-semibold font-display">{p.name}</p>
                        <p className="text-xs text-muted">
                          Age {p.age} &middot; {p.location}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className="text-lg font-bold font-mono"
                        style={{ color: getUrgencyColor(p.urgency_window_days || 99) }}
                      >
                        {p.urgency_window_days}d
                      </p>
                      <p className="text-xs text-muted">
                        {getUrgencyLabel(p.urgency_window_days || 99)}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
