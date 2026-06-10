"use client";

import { useState, useEffect } from "react";
import type { Workflow, WorkflowInsight, Donor, BloodGroup } from "@/lib/types";
import { BLOOD_GROUP_COLORS } from "@/lib/types";
import { Badge } from "@/components/Badge";
import { Card } from "@/components/Card";
import { Brain, Lightning, Check, Phone, MagnifyingGlass, ArrowRight } from "@phosphor-icons/react";
import { api } from "@/lib/api";

export default function CoordinatorPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [insights, setInsights] = useState<WorkflowInsight[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    // Poll every 5 seconds for workflow updates
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  async function fetchData() {
    try {
      const [workflowsData, insightsData] = await Promise.all([
        api.get<Workflow[]>("/api/workflow/active"),
        api.get<WorkflowInsight[]>("/api/workflow/insights"),
      ]);

      setWorkflows(workflowsData);
      setInsights(insightsData);

      // Auto-select first workflow if none selected
      if (!selectedWorkflowId && workflowsData.length > 0) {
        setSelectedWorkflowId(workflowsData[0].workflow_id);
      }

      setError(null);
    } catch (err) {
      console.error("Failed to fetch coordinator data:", err);
      setError("Failed to load workflows. Check backend connection.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRankDonors(workflowId: string) {
    try {
      await api.post(`/api/workflow/${workflowId}/rank-donors`);
      fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to rank donors:", err);
      alert("Failed to rank donors");
    }
  }

  async function handleWhatsAppCampaign(workflowId: string) {
    try {
      await api.post(`/api/workflow/${workflowId}/whatsapp-campaign`);
      fetchData();
    } catch (err) {
      console.error("Failed to start WhatsApp campaign:", err);
      alert("Failed to start WhatsApp campaign");
    }
  }

  async function handleVoiceCampaign(workflowId: string) {
    try {
      await api.post(`/api/workflow/${workflowId}/voice-campaign`);
      fetchData();
    } catch (err) {
      console.error("Failed to start voice campaign:", err);
      alert("Failed to start voice campaign");
    }
  }

  const active = workflows.find((w) => w.workflow_id === selectedWorkflowId);

  const getUrgencyColor = (urgency: string) => {
    if (urgency === "critical" || urgency === "CRITICAL") return "var(--blood)";
    if (urgency === "urgent" || urgency === "URGENT") return "var(--warning)";
    return "var(--positive)";
  };

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-3xl font-bold font-display">Coordinator Command Center</h1>
      <p className="mb-8 text-secondary">
        Unified workflow timeline, donor rankings, and self-learning insights.
      </p>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--blood-pink)] mx-auto mb-4"></div>
            <p className="text-secondary">Loading workflows...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-xl border border-warning/30 bg-warning/5 p-8 text-center">
          <Brain size={48} weight="regular" className="mx-auto mb-4" style={{ color: "var(--warning)" }} />
          <p className="text-lg font-semibold text-warning mb-2">{error}</p>
          <button
            onClick={fetchData}
            className="mt-4 rounded-lg bg-blood px-6 py-3 text-sm font-semibold text-white hover:brightness-110 transition-all"
          >
            Retry
          </button>
        </div>
      )}

      {/* Main Content */}
      {!loading && !error && (
        <>
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left: Active Workflows */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold font-display">Active Workflows ({workflows.length})</h2>
          {workflows.map((wf) => (
            <button
              key={wf.workflow_id}
              onClick={() => setSelectedWorkflowId(wf.workflow_id)}
              className={`w-full rounded-2xl border p-5 text-left transition-all duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                selectedWorkflowId === wf.workflow_id
                  ? "border-blood bg-blood/5"
                  : "border-border bg-card hover:bg-card-hover"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {wf.patient_data && (
                    <Badge type="blood" value={wf.patient_data.blood_group as BloodGroup} />
                  )}
                  <span className="font-semibold font-display">
                    {wf.patient_data?.name || `Patient ${wf.patient_id.slice(-4)}`}
                  </span>
                </div>
                {wf.patient_data && (
                  <span
                    className="text-lg font-bold font-mono"
                    style={{ color: getUrgencyColor(wf.patient_data.urgency) }}
                  >
                    {wf.patient_data.urgency}
                  </span>
                )}
              </div>
              <p className="mt-2 text-xs text-muted">
                Step: {wf.current_step.replace(/_/g, " ")} &middot;{" "}
                {wf.completed_at ? "Done" : "In Progress"}
              </p>
            </button>
          ))}

          {workflows.length === 0 && (
            <Card className="text-center">
              <p className="text-secondary">No active workflows</p>
              <p className="mt-2 text-xs text-muted">
                Start a workflow from the patient page
              </p>
            </Card>
          )}
        </div>

        {/* Center: Workflow Timeline */}
        <div>
          <h2 className="mb-4 text-lg font-bold font-display">
            Workflow: {active?.patient_data?.name || `Patient ${active?.patient_id.slice(-4)}`}
          </h2>
          <Card>
            {active?.steps.map((step, i) => {
              const isLast = i === active.steps.length - 1;
              return (
                <div key={i} className="flex gap-4">
                  {/* Timeline line */}
                  <div className="flex flex-col items-center">
                    <div
                      className={`flex h-4 w-4 items-center justify-center rounded-full border-2 ${
                        step.status === "completed"
                          ? "border-success bg-success"
                          : step.status === "in_progress"
                          ? "border-info bg-info animate-pulse-border-blue"
                          : "border-border bg-surface"
                      }`}
                    >
                      {step.status === "completed" && (
                        <Check size={10} weight="bold" style={{ color: "var(--bg-primary)" }} />
                      )}
                    </div>
                    {!isLast && (
                      <div
                        className={`w-0.5 flex-1 ${
                          step.status === "completed" ? "bg-success" : "bg-border"
                        }`}
                      />
                    )}
                  </div>

                  {/* Step content */}
                  <div className="pb-6 flex-1">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p
                          className={`text-sm font-semibold font-display ${
                            step.status === "in_progress"
                              ? "text-info"
                              : step.status === "completed"
                              ? "text-primary"
                              : "text-muted"
                          }`}
                        >
                          {step.step_name}
                        </p>
                        {step.details && (
                          <p className="mt-1 text-xs text-secondary">
                            {step.details}
                          </p>
                        )}
                        {step.started_at && (
                          <p className="mt-1 text-xs font-mono text-muted">
                            {new Date(step.started_at).toLocaleTimeString()}
                            {step.completed_at && ` → ${new Date(step.completed_at).toLocaleTimeString()}`}
                          </p>
                        )}
                      </div>

                      {/* Action buttons for specific steps */}
                      {step.status === "in_progress" && active && (
                        <div className="flex gap-2">
                          {step.step_name === "AI Donor Matching" && (
                            <button
                              onClick={() => handleRankDonors(active.workflow_id)}
                              className="rounded-lg bg-blood px-3 py-1 text-xs font-semibold text-white hover:brightness-110 transition-colors"
                            >
                              Rank Donors
                            </button>
                          )}
                          {step.step_name === "WhatsApp Campaign" && (
                            <button
                              onClick={() => handleWhatsAppCampaign(active.workflow_id)}
                              className="rounded-lg bg-success px-3 py-1 text-xs font-semibold text-white hover:brightness-110 transition-colors"
                            >
                              Send WhatsApp
                            </button>
                          )}
                          {step.step_name === "Voice Call Campaign" && (
                            <button
                              onClick={() => handleVoiceCampaign(active.workflow_id)}
                              className="rounded-lg bg-info px-3 py-1 text-xs font-semibold text-white hover:brightness-110 transition-colors"
                            >
                              Start Calls
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </Card>
        </div>

        {/* Right: Donor Rankings + Insights */}
        <div className="space-y-6">
          {/* Donor Rankings */}
          <Card>
            <h3 className="mb-4 text-sm font-bold font-display text-secondary">
              Ranked Donors
              {active?.patient_data && (
                <span className="ml-2 text-xs text-muted">
                  ({active.patient_data.blood_group} - {active.patient_data.latitude.toFixed(2)}, {active.patient_data.longitude.toFixed(2)})
                </span>
              )}
            </h3>
            {active?.ranked_donors && active.ranked_donors.length > 0 ? (
              <div className="space-y-2">
                {active.ranked_donors.slice(0, 10).map((donor, i) => (
                  <div
                    key={donor.donor_id}
                    className="flex items-center justify-between rounded-lg bg-surface p-3"
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold font-mono ${
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
                      <div>
                        <p className="text-sm font-semibold font-display">{donor.name}</p>
                        <p className="text-xs text-muted font-mono">
                          {donor.distance_km?.toFixed(1)}km &middot; {((donor.readiness_score || 0) * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                    <Badge type="blood" value={donor.blood_group} />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted text-center py-4">
                No donors ranked yet. Click "Rank Donors" on the workflow.
              </p>
            )}
            <p className="mt-3 text-xs text-muted">
              Score = Eligibility x Reliability x Proximity x Willingness x Availability
            </p>
          </Card>

          {/* Self-Learning Insights */}
          <Card>
            <div className="mb-4 flex items-center gap-2">
              <Brain size={20} weight="regular" style={{ color: "var(--ai)" }} />
              <h3 className="text-sm font-bold font-display text-ai">
                Self-Learning Insights
              </h3>
            </div>
            <div className="space-y-3">
              {insights.map((insight, i) => (
                <div key={i} className="rounded-lg bg-surface p-3">
                  <p className="text-xs font-semibold font-display text-primary">
                    {insight.pattern}
                  </p>
                  <p className="mt-1 text-xs text-secondary">
                    {insight.action}
                  </p>
                  <p className="mt-1 text-xs font-mono text-positive">{insight.result}</p>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-muted">
              Powered by SageMaker retraining + CloudWatch failure logs
            </p>
          </Card>
        </div>
      </div>
        </>
      )}
    </div>
  );
}
