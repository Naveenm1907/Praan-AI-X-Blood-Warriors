"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/Card";
import { Badge } from "@/components/Badge";
import { Warning, Clock, Users, Phone, CheckCircle } from "@phosphor-icons/react";
import Link from "next/link";

export default function WarriorApp() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTasks();
  }, []);

  async function loadTasks() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/tasks/warrior");
      if (!response.ok) throw new Error("Failed to load tasks");
      const data = await response.json();
      setTasks(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
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

  const pendingCount = tasks.filter((t: any) => t.status === "pending").length;
  const inProgressCount = tasks.filter((t: any) => t.status === "in_progress").length;
  const completedCount = tasks.filter((t: any) => t.status === "completed").length;

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Warrior App</h1>
        <p className="text-muted-foreground">Today's tasks and donor outreach</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{pendingCount}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Phone className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{inProgressCount}</p>
              <p className="text-sm text-gray-600">In Progress</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{completedCount}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </div>
        </Card>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <Warning className="w-5 h-5 text-red-600 mt-0.5" />
          <span className="text-red-800">{error}</span>
        </div>
      )}

      <Card>
        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5" />
          Today's Tasks ({tasks.length})
        </h2>
        {loading ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Loading tasks...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
            <p className="text-lg font-semibold mb-2">All caught up!</p>
            <p className="text-gray-600">No pending tasks for today</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task: any) => (
              <Link key={task.id} href={`/warrior/tasks/${task.id}`}>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">{task.patient_name}</h3>
                        <Badge type="blood" value={task.patient_blood_group} />
                        {task.urgency && (
                          <span className={`px-2 py-1 text-xs rounded ${getUrgencyColor(task.urgency)}`}>
                            {task.urgency}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 flex items-center gap-4">
                        <span>Age: {task.patient_age}</span>
                        <span>{task.patient_location}</span>
                        {task.days_until_transfusion !== null && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {task.days_until_transfusion} days until transfusion
                          </span>
                        )}
                      </div>
                    </div>
                    {getStatusBadge(task.status)}
                  </div>

                  <div className="border-t pt-3 mt-3">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-gray-600" />
                        <span className="text-gray-600">
                          {task.assigned_donors?.length || 0} donors assigned
                        </span>
                      </div>
                      {task.assigned_donors && (
                        <div className="flex items-center gap-2">
                          <span className="text-gray-600">
                            {task.assigned_donors.filter((d: any) => d.response === "confirmed").length} confirmed
                          </span>
                          <span className="text-gray-600">•</span>
                          <span className="text-gray-600">
                            {task.assigned_donors.filter((d: any) => d.contacted).length} contacted
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
