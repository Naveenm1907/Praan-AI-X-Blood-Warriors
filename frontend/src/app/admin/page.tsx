"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/Card";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { Warning, Robot, Users, ActivityIcon, Clock, CheckCircle, Play, CircleNotch } from "@phosphor-icons/react";
import Link from "next/link";

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalPatients: 0,
    activeTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
  });
  const [agentStatus, setAgentStatus] = useState<any>(null);
  const [recentPatients, setRecentPatients] = useState([]);
  const [recentTasks, setRecentTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [agentRunning, setAgentRunning] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      // Load patients
      const patientsRes = await fetch("http://localhost:8000/api/patient/patients");
      if (patientsRes.ok) {
        const patients = await patientsRes.json();
        setStats(prev => ({ ...prev, totalPatients: patients.length }));
        setRecentPatients(patients.slice(0, 5));
      }

      // Load tasks
      const tasksRes = await fetch("http://localhost:8000/api/tasks/warrior");
      if (tasksRes.ok) {
        const tasks = await tasksRes.json();
        const active = tasks.filter((t: any) => t.status === "pending" || t.status === "in_progress");
        const completed = tasks.filter((t: any) => t.status === "completed");
        const pending = tasks.filter((t: any) => t.status === "pending");

        setStats(prev => ({
          ...prev,
          activeTasks: active.length,
          completedTasks: completed.length,
          pendingTasks: pending.length,
        }));
        setRecentTasks(tasks.slice(0, 5));
      }

      // Load agent status
      const agentRes = await fetch("http://localhost:8000/api/agent/status");
      if (agentRes.ok) {
        const status = await agentRes.json();
        setAgentStatus(status);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function runAgent() {
    setAgentRunning(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch("http://localhost:8000/api/agent/run-daily", {
        method: "POST",
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Agent run failed");
      }

      const data = await response.json();
      setSuccess(`Agent processed ${data.patients_processed} patients, created ${data.tasks_created} tasks`);

      // Reload dashboard
      await loadDashboard();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAgentRunning(false);
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

  function getStatusBadge(status: string) {
    switch (status) {
      case "pending":
        return <span className="px-2 py-1 text-xs rounded bg-blue-50 text-blue-700 border border-blue-300">Pending</span>;
      case "in_progress":
        return <span className="px-2 py-1 text-xs rounded bg-yellow-50 text-yellow-700 border border-yellow-300">In Progress</span>;
      case "completed":
        return <span className="px-2 py-1 text-xs rounded bg-green-50 text-green-700 border border-green-300">Completed</span>;
      default:
        return <span className="px-2 py-1 text-xs rounded bg-gray-50 text-gray-700 border border-gray-300">{status}</span>;
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6 max-w-7xl">
        <div className="text-center py-12">
          <CircleNotch className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">System overview and AI Agent control</p>
        </div>
        <button
          onClick={runAgent}
          disabled={agentRunning}
          className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {agentRunning ? (
            <>
              <CircleNotch className="w-5 h-5 animate-spin" />
              Agent Running...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Run Agent Now
            </>
          )}
        </button>
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

      <div className="grid grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.totalPatients}</p>
              <p className="text-sm text-gray-600">Total Patients</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.pendingTasks}</p>
              <p className="text-sm text-gray-600">Pending Tasks</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <ActivityIcon className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.activeTasks}</p>
              <p className="text-sm text-gray-600">Active Tasks</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completedTasks}</p>
              <p className="text-sm text-gray-600">Completed Tasks</p>
            </div>
          </div>
        </Card>
      </div>

      {agentStatus && (
        <Card className="mb-6 border-purple-200 bg-purple-50">
          <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2 text-purple-900">
            <Robot className="w-5 h-5" />
            AI Agent Status
          </h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Last Run</p>
              <p className="font-semibold">
                {agentStatus.last_run_date
                  ? new Date(agentStatus.last_run_date).toLocaleString()
                  : "Never"}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Patients Processed</p>
              <p className="font-semibold">{agentStatus.patients_processed || 0}</p>
            </div>
            <div>
              <p className="text-gray-600">Tasks Created</p>
              <p className="font-semibold">{agentStatus.tasks_created || 0}</p>
            </div>
            <div>
              <p className="text-gray-600">Status</p>
              <span className={`px-2 py-1 text-xs rounded ${agentStatus.status === "success" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                {agentStatus.status || "idle"}
              </span>
            </div>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Users className="w-5 h-5" />
              Recent Patients
            </h2>
            <Link href="/admin/patient">
              <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                View All
              </button>
            </Link>
          </div>
          {recentPatients.length === 0 ? (
            <p className="text-gray-600 text-center py-4">No patients yet</p>
          ) : (
            <div className="space-y-3">
              {recentPatients.map((patient: any) => (
                <div key={patient.id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{patient.name}</h4>
                    <div className="flex gap-2">
                      <Badge type="blood" value={patient.blood_group} />
                      {patient.urgency_level && (
                        <span className={`px-2 py-1 text-xs rounded ${getUrgencyColor(patient.urgency_level)}`}>
                          {patient.urgency_level}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-600">
                    Age: {patient.age} • {patient.location}
                    {patient.severity && ` • Severity: ${patient.severity}`}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <ActivityIcon className="w-5 h-5" />
              Recent Tasks
            </h2>
            <Link href="/admin/coordinator">
              <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
                View All
              </button>
            </Link>
          </div>
          {recentTasks.length === 0 ? (
            <p className="text-gray-600 text-center py-4">No tasks yet</p>
          ) : (
            <div className="space-y-3">
              {recentTasks.map((task: any) => (
                <div key={task.id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{task.patient_name}</h4>
                    {getStatusBadge(task.status)}
                  </div>
                  <div className="text-xs text-gray-600">
                    {task.assigned_donors?.length || 0} donors •
                    {task.urgency && ` ${task.urgency}`}
                    {task.created_at && ` • ${new Date(task.created_at).toLocaleDateString()}`}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
