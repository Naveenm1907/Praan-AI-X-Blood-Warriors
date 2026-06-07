"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/Card";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { Warning, Phone, ChatCircle, CheckCircle, Clock, User, Users, MapPin, ActivityIcon } from "@phosphor-icons/react";

export default function TaskDetail() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id;

  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [callingDonor, setCallingDonor] = useState<string | null>(null);

  useEffect(() => {
    if (taskId) {
      loadTask();
    }
  }, [taskId]);

  async function loadTask() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}`);
      if (!response.ok) throw new Error("Failed to load task");
      const data = await response.json();
      setTask(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function callDonor(donor: any) {
    setCallingDonor(donor.donor_id);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("http://localhost:8000/api/voice/call-donor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          donor_id: donor.donor_id,
          patient_name: task?.patient_name || "Patient",
          patient_id: task?.patient_id,
          blood_group: task?.patient_blood_group || "O+",
          workflow_id: task?.workflow_id,
          language: "te",
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Call failed");
      }

      const result = await response.json();
      setSuccess(`Call initiated to ${donor.name}. Call ID: ${result.call_id}`);
      await loadTask();
    } catch (err: any) {
      setError(err.message || "Failed to initiate call");
    } finally {
      setCallingDonor(null);
    }
  }

  async function assignTask() {
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/assign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ warrior_id: 1 }), // Demo: warrior_id=1
      });

      if (!response.ok) throw new Error("Failed to assign task");
      await loadTask();
      setSuccess("Task assigned to you!");
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function updateDonorResponse(donorId: string, response: string) {
    try {
      const res = await fetch(`http://localhost:8000/api/tasks/${taskId}/update-donor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ donor_id: donorId, response }),
      });

      if (!res.ok) throw new Error("Failed to update response");
      await loadTask();
    } catch (err: any) {
      setError(err.message);
    }
  }

  async function completeTask() {
    try {
      const response = await fetch(`http://localhost:8000/api/tasks/${taskId}/complete`, {
        method: "POST",
      });

      if (!response.ok) throw new Error("Failed to complete task");
      setSuccess("Task completed successfully!");
      setTimeout(() => router.push("/warrior"), 1500);
    } catch (err: any) {
      setError(err.message);
    }
  }

  function getUrgencyColor(urgency: string) {
    switch (urgency) {
      case "CRITICAL": return "bg-red-100 text-red-800 border-red-300";
      case "URGENT": return "bg-orange-100 text-orange-800 border-orange-300";
      case "SOON": return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default: return "bg-gray-100 text-gray-800 border-gray-300";
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="text-center py-12">
          <p className="text-gray-600">Loading task...</p>
        </div>
      </div>
    );
  }

  if (error && !task) {
    return (
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <Warning className="w-5 h-5 text-red-600 mt-0.5" />
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  if (!task) return null;

  const assignedDonors = task.assigned_donors || [];
  const contactedCount = assignedDonors.filter((d: any) => d.contacted).length;
  const confirmedCount = assignedDonors.filter((d: any) => d.response === "confirmed").length;

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <button
          onClick={() => router.push("/warrior")}
          className="mb-4 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          ← Back to Tasks
        </button>
        <h1 className="text-3xl font-bold mb-2">Task Details</h1>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <Warning className="w-5 h-5 text-red-600 mt-0.5" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
          <span className="text-green-800">{success}</span>
        </div>
      )}

      <Card className="mb-6">
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-3">
          <User className="w-6 h-6" />
          Patient Information
        </h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold">{task.patient_name}</h3>
              <p className="text-gray-600">Age: {task.patient_age}</p>
            </div>
            <div className="flex gap-2">
              <Badge type="blood" value={task.patient_blood_group} />
              {task.urgency && (
                <span className={`px-2 py-1 text-xs rounded ${getUrgencyColor(task.urgency)}`}>
                  {task.urgency}
                </span>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-3 border-t">
            <div>
              <p className="text-sm text-gray-600 mb-1">Location</p>
              <p className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                {task.patient_location}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Phone</p>
              <p className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                {task.patient_phone}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Severity</p>
              <p className="flex items-center gap-2">
                <ActivityIcon className="w-4 h-4" />
                {task.patient_severity || "Not assessed"}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Days Until Transfusion</p>
              <p className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                {task.days_until_transfusion !== null ? `${task.days_until_transfusion} days` : "Unknown"}
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold flex items-center gap-3">
            <Users className="w-6 h-6" />
            Assigned Donors ({assignedDonors.length})
          </h2>
          <div className="text-sm text-gray-600">
            {contactedCount} contacted • {confirmedCount} confirmed
          </div>
        </div>
        {assignedDonors.length === 0 ? (
          <p className="text-gray-600 text-center py-4">No donors assigned</p>
        ) : (
          <div className="space-y-3">
            {assignedDonors.map((donor: any, index: number) => (
              <div key={donor.donor_id} className="p-4 border rounded-lg">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono text-sm text-gray-600">
                        #{index + 1}
                      </span>
                      <h4 className="font-semibold">{donor.name}</h4>
                      <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">
                        ID: {donor.donor_id}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Readiness Score: <span className="font-semibold text-gray-900">{(donor.score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  {donor.contacted ? (
                    <span className={`px-2 py-1 text-xs rounded ${donor.response === "confirmed" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                      {donor.response}
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs rounded bg-blue-50 text-blue-700 border border-blue-300">
                      Not contacted
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 pt-3 border-t">
                  <button
                    onClick={() => callDonor(donor)}
                    disabled={donor.contacted || callingDonor === donor.donor_id}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Phone className="w-4 h-4 inline mr-2" />
                    {callingDonor === donor.donor_id ? "Calling..." : "Call"}
                  </button>
                  <button
                    onClick={() => window.open(`https://wa.me/${donor.phone || ""}`, "_blank")}
                    disabled={donor.contacted}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChatCircle className="w-4 h-4 inline mr-2" />
                    WhatsApp
                  </button>

                  {!donor.contacted && (
                    <select
                      onChange={(e) => updateDonorResponse(donor.donor_id, e.target.value)}
                      className="w-40 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Mark response</option>
                      <option value="confirmed">✓ Confirmed</option>
                      <option value="declined">✗ Declined</option>
                      <option value="no_answer">No answer</option>
                    </select>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <div className="flex gap-3">
        {task.status === "pending" && (
          <Button variant="primary" onClick={assignTask} className="flex-1">
            <User className="w-4 h-4 mr-2" />
            Assign to Me
          </Button>
        )}

        {task.status === "in_progress" && (
          <Button variant="primary" onClick={completeTask} className="flex-1">
            <CheckCircle className="w-4 h-4 mr-2" />
            Complete Task
          </Button>
        )}

        {task.status === "completed" && (
          <div className="flex-1 p-4 bg-green-50 border border-green-200 rounded-lg text-center">
            <CheckCircle className="w-5 h-5 text-green-600 inline mb-2" />
            <p className="text-green-800 font-semibold">Task Completed</p>
            <p className="text-sm text-green-700">{confirmedCount} donors confirmed</p>
          </div>
        )}
      </div>
    </div>
  );
}
