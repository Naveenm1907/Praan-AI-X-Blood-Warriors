"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import type { BloodGroup, Patient } from "@/lib/types";
import { BLOOD_GROUPS, BLOOD_GROUP_COLORS } from "@/lib/types";

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
  }
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
    if (days <= 7) return "var(--orange)";
    return "var(--green)";
  };

  const getUrgencyLabel = (days: number) => {
    if (days <= 3) return "URGENT";
    if (days <= 7) return "MODERATE";
    return "SCHEDULED";
  };

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold">Patient Onboarding</h1>
      <p className="mb-8 text-[var(--text-secondary)]">
        Register patient, upload medical report, and calculate transfusion urgency window.
      </p>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Form */}
        <div className="rounded-2xl border border-border bg-card p-8">
          <h2 className="mb-6 text-xl font-bold">Patient Registration</h2>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                  placeholder="Patient name"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Age</label>
                <input
                  type="number"
                  value={form.age}
                  onChange={(e) => setForm({ ...form, age: e.target.value })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                  placeholder="Age"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Blood Group</label>
                <select
                  value={form.blood_group}
                  onChange={(e) => setForm({ ...form, blood_group: e.target.value as BloodGroup })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                >
                  {BLOOD_GROUPS.map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Location</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                  placeholder="City/District"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Last Transfusion</label>
                <input
                  type="date"
                  value={form.last_transfusion_date}
                  onChange={(e) => setForm({ ...form, last_transfusion_date: e.target.value })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm text-[var(--text-secondary)]">Cycle Length (days)</label>
                <input
                  type="number"
                  value={form.cycle_length_days}
                  onChange={(e) => setForm({ ...form, cycle_length_days: e.target.value })}
                  className="w-full rounded-xl border border-border bg-surface px-4 py-3 text-sm text-[var(--text-primary)] focus:border-info focus:outline-none"
                  placeholder="21"
                />
              </div>
            </div>

            {/* Medical Report Upload */}
            <div>
              <label className="mb-1 block text-sm text-[var(--text-secondary)]">Medical Report</label>
              <div
                onClick={handleUpload}
                className="cursor-pointer rounded-xl border-2 border-dashed border-border bg-surface p-8 text-center transition-all hover:border-blood"
              >
                {uploading ? (
                  <div>
                    <p className="text-sm text-[var(--ai)]">Textract scanning report...</p>
                    <p className="mt-1 text-xs text-[var(--text-muted)]">Extracting Hb, MCV, MCH, Ferritin</p>
                  </div>
                ) : ocrResult ? (
                  <p className="text-sm text-success">Report scanned successfully</p>
                ) : (
                  <div>
                    <p className="text-2xl">&#128196;</p>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">
                      Click to upload PDF/Image (simulated Textract OCR)
                    </p>
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={!form.name || !form.age || !form.last_transfusion_date || !ocrResult}
              className="w-full rounded-xl bg-blood py-3 text-sm font-semibold text-white transition-all hover:brightness-110 disabled:opacity-40"
            >
              Register Patient & Calculate Urgency
            </button>
          </div>
        </div>

        {/* Right side: OCR Results + Urgency */}
        <div className="space-y-6">
          {/* OCR Results */}
          {ocrResult && (
            <div className="rounded-2xl border border-border bg-card p-8">
              <h2 className="mb-4 text-xl font-bold">Medical Report Values</h2>
              <p className="mb-4 text-xs text-[var(--ai)]">Extracted by AWS Textract OCR</p>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { label: "Hb", value: `${ocrResult.hb} g/dL`, low: ocrResult.hb < 10 },
                  { label: "MCV", value: `${ocrResult.mcv} fL`, low: ocrResult.mcv < 80 },
                  { label: "Ferritin", value: `${ocrResult.ferritin} ng/mL`, low: ocrResult.ferritin < 30 },
                  { label: "MCH", value: `${ocrResult.mch} pg`, low: ocrResult.mch < 27 },
                ].map((item) => (
                  <div
                    key={item.label}
                    className={`rounded-xl border p-4 text-center ${
                      item.low ? "border-blood/30 bg-blood/5" : "border-border bg-surface"
                    }`}
                  >
                    <p className="text-xs text-[var(--text-muted)]">{item.label}</p>
                    <p className="mt-1 text-xl font-bold">{item.value}</p>
                    {item.low && (
                      <span className="text-xs text-blood">Low</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Urgency Window */}
          {newPatient && newPatient.urgency_window_days && (
            <div
              className="rounded-2xl border-l-4 bg-card p-8"
              style={{ borderColor: getUrgencyColor(newPatient.urgency_window_days) }}
            >
              <h2 className="mb-2 text-xl font-bold">Transfusion Urgency Window</h2>
              <div className="mt-4 text-center">
                <p className="font-mono text-4xl font-bold" style={{ color: getUrgencyColor(newPatient.urgency_window_days) }}>
                  {newPatient.urgency_window_days} DAYS
                </p>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  until next transfusion needed
                </p>
              </div>
              <div className="mt-6 flex items-center justify-center">
                <span
                  className="rounded-full px-4 py-1 text-sm font-bold"
                  style={{
                    background: `${getUrgencyColor(newPatient.urgency_window_days)}20`,
                    color: getUrgencyColor(newPatient.urgency_window_days),
                  }}
                >
                  {getUrgencyLabel(newPatient.urgency_window_days)} — Donor search starts NOW
                </span>
              </div>
              <div className="mt-6 flex gap-3">
                <a
                  href="/blood-bank"
                  className="flex-1 rounded-xl border border-border bg-surface py-3 text-center text-sm font-semibold text-[var(--text-secondary)] hover:bg-card-hover"
                >
                  Check Blood Banks
                </a>
                <a
                  href="/donor-outreach"
                  className="flex-1 rounded-xl bg-blood py-3 text-center text-sm font-semibold text-white hover:brightness-110"
                >
                  Start Voice Calls
                </a>
              </div>
            </div>
          )}

          {/* Existing Patients */}
          <div className="rounded-2xl border border-border bg-card p-8">
            <h2 className="mb-4 text-xl font-bold">Active Patients</h2>
            <div className="space-y-3">
              {patients
                .sort((a, b) => (a.urgency_window_days || 99) - (b.urgency_window_days || 99))
                .map((p) => (
                  <div
                    key={p.patient_id}
                    className="flex items-center justify-between rounded-xl border border-border bg-surface p-4"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className="rounded-lg px-2 py-1 text-xs font-bold"
                        style={{
                          background: `${BLOOD_GROUP_COLORS[p.blood_group]}20`,
                          color: BLOOD_GROUP_COLORS[p.blood_group],
                        }}
                      >
                        {p.blood_group}
                      </span>
                      <div>
                        <p className="text-sm font-semibold">{p.name}</p>
                        <p className="text-xs text-[var(--text-muted)]">
                          Age {p.age} &middot; {p.location}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className="font-mono text-lg font-bold"
                        style={{ color: getUrgencyColor(p.urgency_window_days || 99) }}
                      >
                        {p.urgency_window_days}d
                      </p>
                      <p className="text-xs text-[var(--text-muted)]">
                        {getUrgencyLabel(p.urgency_window_days || 99)}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )};
