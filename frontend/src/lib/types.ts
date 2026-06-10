export interface Patient {
  id: number;
  patient_code?: string;
  name: string;
  age: number;
  sex?: string;
  gender: string;
  weight_kg?: number;
  blood_group: BloodGroup;
  phone: string;
  location: string;
  spleen_enlargement?: string;
  last_transfusion_date?: string;
  transfusion_interval_days?: number;
  hb_level?: number;
  rbc_count?: number;
  mcv_level?: number;
  mch_level?: number;
  mchc_level?: number;
  rdw_pct?: number;
  ferritin_level?: number;
  hb_a_pct?: number;
  hb_a2?: number;
  hb_f?: number;
  mentzer_index?: number;
  wbc_count?: number;
  platelet_count?: number;
  hb_post_transfusion?: number;
  hb_drop_rate_per_day?: number;
  hb_transfusion_threshold?: number;
  days_since_last_transfusion?: number;
  units_per_session?: number;
  avg_transfusion_interval_days?: number;
  days_until_next_transfusion?: number;
  severity?: string;
  severity_score?: number;
  urgency_level?: string;
  days_until_transfusion?: number;
  next_transfusion_date?: string;
  ocr_text?: string;
  ocr_confidence?: number;
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
}

export interface PatientAnalysis {
  patient: Patient;
  analysis: {
    rule_severity?: string;
    ml_severity?: string;
    confidence?: number;
    probabilities?: Record<string, number>;
    method?: string;
  };
  transfusion_days?: number;
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
  patient_data?: {
    patient_id: string;
    name: string;
    blood_group: string;
    latitude: number;
    longitude: number;
    urgency: string;
  };
  current_step: string;
  steps: WorkflowStep[];
  scoring_method?: string;
  ranked_donors?: Donor[];
  whatsapp_campaign?: Array<{
    donor_id: string;
    name: string;
    phone: string;
    status: string;
    sent_at: string;
    readiness_score?: number;
  }>;
  voice_campaign?: Array<{
    donor_id: string;
    name: string;
    phone: string;
    status: string;
    initiated_at: string;
    readiness_score?: number;
  }>;
  donor_responses?: Array<{
    donor_id: string;
    response: string;
    recorded_at: string;
  }>;
  created_at: string;
  completed_at?: string;
}

export interface WorkflowInsight {
  pattern: string;
  action: string;
  result: string;
}

export interface WorkflowStep {
  step_name: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  started_at?: string;
  completed_at?: string;
  details?: string;
}

export type BloodGroup = "O+" | "O-" | "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-";

export const BLOOD_GROUPS: BloodGroup[] = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"];

export const BLOOD_GROUP_COLORS: Record<BloodGroup, string> = {
  "O+": "#f14163",
  "O-": "#c42d4a",
  "A+": "#4190e8",
  "A-": "#1fa58a",
  "B+": "#f59e42",
  "B-": "#2fb86e",
  "AB+": "#8a4ac4",
  "AB-": "#6b4a52",
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
