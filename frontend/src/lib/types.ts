export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  blood_group: BloodGroup;
  location: string;
  latitude: number;
  longitude: number;
  last_transfusion_date: string;
  cycle_length_days: number;
  hb_level?: number;
  ferritin_level?: number;
  mcv_level?: number;
  urgency_window_days?: number;
  created_at: string;
}

export interface Donor {
  donor_id: string;
  name: string;
  blood_group: BloodGroup;
  phone: string;
  language: string;
  location: string;
  latitude: number;
  longitude: number;
  last_donation_date: string;
  total_donations: number;
  total_calls: number;
  calls_to_donations_ratio: number;
  eligibility_status: string;
  readiness_score?: number;
  distance_km?: number;
}

export interface BloodBank {
  bank_id: string;
  name: string;
  district: string;
  state: string;
  inventory: Record<string, { units_available: number; expiry_date: string; reserved_count: number }>;
  contact_phone: string;
}

export interface CallCampaign {
  campaign_id: string;
  patient_id: string;
  donor_ids: string[];
  status: "pending" | "calling" | "completed" | "cancelled";
  responses: Record<string, CallResponse>;
  language: string;
  target_count: number;
  confirmed_count: number;
  started_at: string;
}

export interface CallResponse {
  status: "pending" | "calling" | "connected" | "confirmed" | "declined" | "no_answer";
  timestamp?: string;
  retry_count: number;
}

export interface Workflow {
  workflow_id: string;
  patient_id: string;
  current_step: string;
  steps: WorkflowStep[];
  created_at: string;
  completed_at?: string;
}

export interface WorkflowStep {
  step_name: string;
  status: "pending" | "active" | "completed" | "failed";
  started_at?: string;
  completed_at?: string;
  details?: string;
}

export type BloodGroup = "O+" | "O-" | "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-";

export const BLOOD_GROUPS: BloodGroup[] = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"];

export const BLOOD_GROUP_COLORS: Record<BloodGroup, string> = {
  "O+": "#FD6666",
  "O-": "#FF5678",
  "A+": "#41A7F1",
  "A-": "#64FFE3",
  "B+": "#FCAA49",
  "B-": "#29D64F",
  "AB+": "#AE41F1",
  "AB-": "#FFFFFF",
};

export const COMPATIBLE_DONORS: Record<BloodGroup, BloodGroup[]> = {
  "O+": ["O+", "O-"],
  "O-": ["O-"],
  "A+": ["A+", "A-", "O+", "O-"],
  "A-": ["A-", "O-"],
  "B+": ["B+", "B-", "O+", "O-"],
  "B-": ["B-", "O-"],
  "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
  "AB-": ["A-", "B-", "AB-", "O-"],
};
