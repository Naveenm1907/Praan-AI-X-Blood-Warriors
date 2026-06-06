"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Patient {
  id: string;
  name: string;
  age: number;
  blood_group: string;
  location: string;
  last_transfusion_date: string | null;
  created_at: string;
}

interface ReportResult {
  patient_id: string;
  severity: string;
  severity_score: number;
  transfusion_date: string;
  days_until_transfusion: number;
  urgency_level: string;
  extracted_values: Record<string, number>;
  recommendation: string;
}

export default function PatientPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [reportResult, setReportResult] = useState<ReportResult | null>(null);
  const [processingReport, setProcessingReport] = useState(false);

  // Form state
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [bloodGroup, setBloodGroup] = useState("");
  const [location, setLocation] = useState("");
  const [lastTransfusion, setLastTransfusion] = useState("");
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    fetchPatients();
  }, []);

  async function fetchPatients() {
    try {
      const data = await api.get<Patient[]>("/api/patient/patients");
      setPatients(data);
    } catch (error) {
      console.error("Failed to fetch patients:", error);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      // Step 1: Register patient
      const patient = await api.post<Patient>("/api/patient/patients", {
        name,
        age: parseInt(age),
        gender: "Not Specified",
        blood_group: bloodGroup,
        phone: "0000000000",
        location,
        last_transfusion_date: lastTransfusion || null,
      });

      setSelectedPatient(patient);
      setPatients((prev) => [...prev, patient]);

      // Step 2: Upload and process medical report
      if (file) {
        setProcessingReport(true);
        const formData = new FormData();
        formData.append("file", file);
        formData.append("use_mock_ocr", "true");

        const result = await api.upload<ReportResult>(
          `/api/patient/patients/${patient.id}/medical-report`,
          formData
        );

        setReportResult(result);
        setProcessingReport(false);
      }

      // Reset form
      setName("");
      setAge("");
      setBloodGroup("");
      setLocation("");
      setLastTransfusion("");
      setFile(null);
    } catch (error) {
      console.error("Failed to register patient:", error);
      alert("Failed to register patient. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function getUrgencyColor(urgency: string): string {
    const colors: Record<string, string> = {
      critical: "#dc2626",
      urgent: "#ea580c",
      soon: "#ca8a04",
      scheduled: "#16a34a",
      not_needed: "#6b7280",
    };
    return colors[urgency] || "#6b7280";
  }

  function getSeverityColor(severity: string): string {
    const colors: Record<string, string> = {
      "Severe": "#dc2626",
      "Moderate-Severe": "#ea580c",
      "Moderate": "#ca8a04",
      "Mild": "#16a34a",
      "No Thalassemia": "#6b7280",
    };
    return colors[severity] || "#6b7280";
  }

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-[var(--text-primary)] mb-4">
            Patient Registration
          </h1>
          <p className="text-xl text-[var(--text-secondary)]">
            Register patients and analyze medical reports with AI-powered severity classification
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Registration Form */}
          <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
            <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-6">
              Register New Patient
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Patient Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                  placeholder="Enter patient name"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    Age
                  </label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                    placeholder="Age"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    Blood Group
                  </label>
                  <select
                    value={bloodGroup}
                    onChange={(e) => setBloodGroup(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                  >
                    <option value="">Select</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                  className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                  placeholder="City, State"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Last Transfusion Date (Optional)
                </label>
                <input
                  type="date"
                  value={lastTransfusion}
                  onChange={(e) => setLastTransfusion(e.target.value)}
                  className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Medical Report Image
                </label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] file:mr-4 file:py-2 file:px-4 file:border-0 file:bg-[#f14163] file:text-white file:cursor-pointer"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-[#f14163] text-white font-semibold hover:bg-[#e83a5c] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Registering..." : "Register Patient & Analyze Report"}
              </button>
            </form>
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            {/* Processing Status */}
            {processingReport && (
              <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                <div className="flex items-center gap-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#f14163]"></div>
                  <div>
                    <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                      Processing Medical Report
                    </h3>
                    <p className="text-sm text-[var(--text-secondary)]">
                      Extracting values and analyzing severity...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Report Results */}
            {reportResult && !processingReport && (
              <>
                {/* Severity Classification */}
                <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                  <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                    Severity Classification
                  </h3>

                  <div className="flex items-center gap-4 mb-6">
                    <div
                      className="px-6 py-3 text-white font-bold text-lg"
                      style={{ backgroundColor: getSeverityColor(reportResult.severity) }}
                    >
                      {reportResult.severity}
                    </div>
                    <div className="text-[var(--text-secondary)]">
                      Score: <span className="font-mono font-bold">{reportResult.severity_score}</span>
                    </div>
                  </div>

                  <p className="text-[var(--text-secondary)] mb-4">
                    {reportResult.recommendation}
                  </p>
                </div>

                {/* Transfusion Estimation */}
                <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                  <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                    Transfusion Schedule
                  </h3>

                  <div className="grid grid-cols-2 gap-6 mb-6">
                    <div>
                      <div className="text-sm text-[var(--text-secondary)] mb-2">
                        Days Until Transfusion
                      </div>
                      <div
                        className="text-4xl font-bold font-mono"
                        style={{ color: getUrgencyColor(reportResult.urgency_level) }}
                      >
                        {reportResult.days_until_transfusion} days
                      </div>
                    </div>

                    <div>
                      <div className="text-sm text-[var(--text-secondary)] mb-2">
                        Estimated Date
                      </div>
                      <div className="text-2xl font-semibold text-[var(--text-primary)]">
                        {new Date(reportResult.transfusion_date).toLocaleDateString("en-US", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </div>
                    </div>
                  </div>

                  <div
                    className="px-4 py-3 inline-block text-white font-semibold uppercase tracking-wider text-sm"
                    style={{ backgroundColor: getUrgencyColor(reportResult.urgency_level) }}
                  >
                    Urgency: {reportResult.urgency_level}
                  </div>
                </div>

                {/* Extracted Values */}
                {reportResult.extracted_values && (
                  <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                    <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                      Extracted Values
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(reportResult.extracted_values).map(([key, value]) => (
                        <div key={key} className="bg-[var(--bg-surface)] p-4">
                          <div className="text-sm text-[var(--text-secondary)] mb-1">
                            {key.toUpperCase()}
                          </div>
                          <div className="text-2xl font-mono font-bold text-[var(--text-primary)]">
                            {value}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Next Steps */}
                <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                  <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                    Next Steps
                  </h3>

                  <div className="space-y-3">
                    <Link
                      href={`/donors?patient_id=${reportResult.patient_id}`}
                      className="block w-full py-3 bg-[#f14163] text-white text-center font-semibold hover:bg-[#e83a5c] transition-colors"
                    >
                      Find Matching Donors
                    </Link>

                    <Link
                      href={`/blood-bank?patient_id=${reportResult.patient_id}`}
                      className="block w-full py-3 border border-[#f14163] text-[#f14163] text-center font-semibold hover:bg-[#f14163] hover:text-white transition-colors"
                    >
                      Check Blood Bank Inventory
                    </Link>
                  </div>
                </div>
              </>
            )}

            {/* No Report Yet */}
            {!reportResult && !processingReport && (
              <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)] text-center">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">
                  No Report Analyzed Yet
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Register a patient and upload a medical report to see AI-powered analysis
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Registered Patients List */}
        {patients.length > 0 && (
          <div className="mt-12 bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
            <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-6">
              Registered Patients ({patients.length})
            </h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border-color)]">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Name
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Age
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Blood Group
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Location
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Registered
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient) => (
                    <tr
                      key={patient.id}
                      className="border-b border-[var(--border-color)] hover:bg-[var(--bg-surface)] transition-colors"
                    >
                      <td className="py-3 px-4 text-[var(--text-primary)]">{patient.name}</td>
                      <td className="py-3 px-4 text-[var(--text-primary)]">{patient.age}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-[#f14163]/20 text-[#f14163] text-sm font-mono">
                          {patient.blood_group}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-[var(--text-primary)]">{patient.location}</td>
                      <td className="py-3 px-4 text-sm text-[var(--text-secondary)]">
                        {new Date(patient.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
