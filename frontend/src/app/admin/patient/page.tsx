"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Patient {
  id: number;
  name: string;
  age: number;
  gender: string;
  blood_group: string;
  phone: string;
  location: string;
  last_transfusion_date: string | null;
  transfusion_interval_days: number;
  hb_level?: number;
  mcv_level?: number;
  mch_level?: number;
  mchc_level?: number;
  rbc_count?: number;
  wbc_count?: number;
  platelet_count?: number;
  ferritin_level?: number;
  hb_a2?: number;
  hb_f?: number;
  severity?: string;
  severity_score?: number;
  urgency_level?: string;
  days_until_transfusion?: number;
  next_transfusion_date?: string;
  created_at: string;
  updated_at?: string;
}

interface MedicalReportResponse {
  message: string;
  patient: Patient;
}

export default function PatientPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [processingReport, setProcessingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Not Specified");
  const [bloodGroup, setBloodGroup] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState("");
  const [lastTransfusion, setLastTransfusion] = useState("");
  const [transfusionInterval, setTransfusionInterval] = useState("28");
  const [file, setFile] = useState<File | null>(null);

  // Manual blood parameters
  const [hbLevel, setHbLevel] = useState("");
  const [mcvLevel, setMcvLevel] = useState("");
  const [ferritinLevel, setFerritinLevel] = useState("");

  useEffect(() => {
    fetchPatients();
  }, []);

  async function fetchPatients() {
    try {
      const data = await api.get<Patient[]>("/api/patient/patients");
      setPatients(data);
    } catch (error) {
      console.error("Failed to fetch patients:", error);
      setError("Failed to load patients. Check backend connection.");
    }
  }

  async function startWorkflow(patientId: number) {
    try {
      const result = await api.post<{ workflow_id: string }>(
        `/api/workflow/start-for-patient/${patientId}`
      );
      alert(`Workflow ${result.workflow_id} created! Redirecting to Coordinator...`);
      window.location.href = "/admin/coordinator";
    } catch (err) {
      console.error("Failed to start workflow:", err);
      alert("Failed to start workflow. Please try again.");
    }
  }

  async function startWorkflow(patientId: number) {
    try {
      await api.post(`/api/workflow/start-for-patient/${patientId}`);
      alert("Workflow started! Redirecting to Coordinator...");
      window.location.href = "/admin/coordinator";
    } catch (err) {
      console.error("Failed to start workflow:", err);
      alert("Failed to start workflow");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Step 1: Register patient
      const patient = await api.post<Patient>("/api/patient/patients", {
        name,
        age: parseInt(age),
        gender,
        blood_group: bloodGroup,
        phone: phone || "0000000000",
        location,
        last_transfusion_date: lastTransfusion || null,
        transfusion_interval_days: parseInt(transfusionInterval) || 28,
        hb_level: hbLevel ? parseFloat(hbLevel) : null,
        mcv_level: mcvLevel ? parseFloat(mcvLevel) : null,
        ferritin_level: ferritinLevel ? parseFloat(ferritinLevel) : null,
      });

      setSelectedPatient(patient);
      setPatients((prev) => [...prev, patient]);

      // Step 2: Upload and process medical report
      if (file) {
        setProcessingReport(true);
        const formData = new FormData();
        formData.append("file", file);

        const result = await api.upload<MedicalReportResponse>(
          `/api/patient/patients/${patient.id}/medical-report`,
          formData
        );

        setSelectedPatient(result.patient);
        setProcessingReport(false);
      }

      // Reset form
      setName("");
      setAge("");
      setGender("Not Specified");
      setBloodGroup("");
      setPhone("");
      setLocation("");
      setLastTransfusion("");
      setTransfusionInterval("28");
      setFile(null);
      setHbLevel("");
      setMcvLevel("");
      setFerritinLevel("");
    } catch (error) {
      console.error("Failed to register patient:", error);
      setError("Failed to register patient. Please try again.");
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

        {/* Error Banner */}
        {error && (
          <div className="mb-8 rounded-xl border border-red-500/30 bg-red-500/5 p-6">
            <p className="text-lg font-semibold text-red-600">{error}</p>
            <button
              onClick={fetchPatients}
              className="mt-4 rounded-lg bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
            >
              Retry
            </button>
          </div>
        )}

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

              <div className="grid grid-cols-3 gap-4">
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
                    Gender
                  </label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                    <option value="Not Specified">Not Specified</option>
                  </select>
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

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                    placeholder="Phone number"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    Transfusion Interval (days)
                  </label>
                  <input
                    type="number"
                    value={transfusionInterval}
                    onChange={(e) => setTransfusionInterval(e.target.value)}
                    className="w-full px-4 py-3 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] focus:border-[#f14163] focus:outline-none"
                    placeholder="28"
                  />
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

              {/* Manual Blood Parameters */}
              <div className="border-t border-[var(--border-color)] pt-6">
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">
                  Blood Parameters (Optional - Manual Entry)
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
                      Hb Level (g/dL)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={hbLevel}
                      onChange={(e) => setHbLevel(e.target.value)}
                      className="w-full px-3 py-2 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] text-sm focus:border-[#f14163] focus:outline-none"
                      placeholder="7.5"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
                      MCV (fL)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={mcvLevel}
                      onChange={(e) => setMcvLevel(e.target.value)}
                      className="w-full px-3 py-2 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] text-sm focus:border-[#f14163] focus:outline-none"
                      placeholder="65"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-2">
                      Ferritin (ng/mL)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={ferritinLevel}
                      onChange={(e) => setFerritinLevel(e.target.value)}
                      className="w-full px-3 py-2 bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)] text-sm focus:border-[#f14163] focus:outline-none"
                      placeholder="120"
                    />
                  </div>
                </div>
                <p className="mt-2 text-xs text-[var(--text-muted)]">
                  Or upload medical report image for automatic OCR extraction
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  Medical Report Image (Optional - OCR)
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

            {/* Patient Results */}
            {selectedPatient && !processingReport && (
              <>
                {/* Severity Classification */}
                {selectedPatient.severity && (
                  <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                    <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                      Severity Classification
                    </h3>

                    <div className="flex items-center gap-4 mb-6">
                      <div
                        className="px-6 py-3 text-white font-bold text-lg"
                        style={{ backgroundColor: getSeverityColor(selectedPatient.severity) }}
                      >
                        {selectedPatient.severity}
                      </div>
                      {selectedPatient.severity_score && (
                        <div className="text-[var(--text-secondary)]">
                          Score: <span className="font-mono font-bold">{selectedPatient.severity_score.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Transfusion Estimation */}
                {selectedPatient.urgency_level && (
                  <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                    <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                      Transfusion Schedule
                    </h3>

                    <div className="grid grid-cols-2 gap-6 mb-6">
                      {selectedPatient.days_until_transfusion && (
                        <div>
                          <div className="text-sm text-[var(--text-secondary)] mb-2">
                            Days Until Transfusion
                          </div>
                          <div
                            className="text-4xl font-bold font-mono"
                            style={{ color: getUrgencyColor(selectedPatient.urgency_level) }}
                          >
                            {selectedPatient.days_until_transfusion} days
                          </div>
                        </div>
                      )}

                      {selectedPatient.next_transfusion_date && (
                        <div>
                          <div className="text-sm text-[var(--text-secondary)] mb-2">
                            Estimated Date
                          </div>
                          <div className="text-2xl font-semibold text-[var(--text-primary)]">
                            {new Date(selectedPatient.next_transfusion_date).toLocaleDateString("en-US", {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            })}
                          </div>
                        </div>
                      )}
                    </div>

                    <div
                      className="px-4 py-3 inline-block text-white font-semibold uppercase tracking-wider text-sm"
                      style={{ backgroundColor: getUrgencyColor(selectedPatient.urgency_level) }}
                    >
                      Urgency: {selectedPatient.urgency_level}
                    </div>
                  </div>
                )}

                {/* Blood Parameters */}
                {(selectedPatient.hb_level || selectedPatient.mcv_level || selectedPatient.ferritin_level) && (
                  <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)]">
                    <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">
                      Blood Parameters
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                      {selectedPatient.hb_level && (
                        <div className="bg-[var(--bg-surface)] p-4">
                          <div className="text-sm text-[var(--text-secondary)] mb-1">Hb Level</div>
                          <div className="text-2xl font-mono font-bold text-[var(--text-primary)]">
                            {selectedPatient.hb_level} g/dL
                          </div>
                        </div>
                      )}
                      {selectedPatient.mcv_level && (
                        <div className="bg-[var(--bg-surface)] p-4">
                          <div className="text-sm text-[var(--text-secondary)] mb-1">MCV</div>
                          <div className="text-2xl font-mono font-bold text-[var(--text-primary)]">
                            {selectedPatient.mcv_level} fL
                          </div>
                        </div>
                      )}
                      {selectedPatient.ferritin_level && (
                        <div className="bg-[var(--bg-surface)] p-4">
                          <div className="text-sm text-[var(--text-secondary)] mb-1">Ferritin</div>
                          <div className="text-2xl font-mono font-bold text-[var(--text-primary)]">
                            {selectedPatient.ferritin_level} ng/mL
                          </div>
                        </div>
                      )}
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
                      href={`/donors?patient_id=${selectedPatient.id}&blood_group=${selectedPatient.blood_group}`}
                      className="block w-full py-3 bg-[#f14163] text-white text-center font-semibold hover:bg-[#e83a5c] transition-colors"
                    >
                      Find Matching Donors
                    </Link>

                    <Link
                      href={`/blood-bank?blood_group=${selectedPatient.blood_group}`}
                      className="block w-full py-3 border border-[#f14163] text-[#f14163] text-center font-semibold hover:bg-[#f14163] hover:text-white transition-colors"
                    >
                      Check Blood Bank Inventory
                    </Link>

                    <Link
                      href={`/coordinator`}
                      className="block w-full py-3 border border-[var(--border-color)] text-[var(--text-secondary)] text-center font-semibold hover:bg-[var(--bg-surface)] transition-colors"
                    >
                      View in Coordinator Dashboard
                    </Link>
                  </div>
                </div>
              </>
            )}

            {/* No Patient Yet */}
            {!selectedPatient && !processingReport && (
              <div className="bg-[var(--bg-card)] p-8 border border-[var(--border-color)] text-center">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-2">
                  No Patient Registered Yet
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Fill out the form and upload a medical report to see AI-powered analysis
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
                      Severity
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Urgency
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Registered
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-[var(--text-secondary)]">
                      Action
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
                      <td className="py-3 px-4">
                        {patient.severity && (
                          <span
                            className="px-2 py-1 text-xs font-semibold text-white"
                            style={{ backgroundColor: getSeverityColor(patient.severity) }}
                          >
                            {patient.severity}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        {patient.urgency_level && (
                          <span
                            className="px-2 py-1 text-xs font-semibold text-white uppercase"
                            style={{ backgroundColor: getUrgencyColor(patient.urgency_level) }}
                          >
                            {patient.urgency_level}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-[var(--text-secondary)]">
                        {patient.created_at && new Date(patient.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => startWorkflow(patient.id)}
                          className="px-3 py-1 text-sm bg-[#f14163] text-white rounded hover:bg-[#e83a5c] transition-colors"
                        >
                          Start Workflow
                        </button>
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
