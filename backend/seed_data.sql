-- ============================================
-- PRAAN AI - Donors Table
-- Matches Dataset.md schema (Blood Warriors)
-- 30 sample records based on dataset format
-- ============================================

CREATE TABLE IF NOT EXISTS donors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL UNIQUE,
    bridge_id VARCHAR(64),
    role VARCHAR(50) NOT NULL DEFAULT 'Emergency Donor',
    role_status BOOLEAN DEFAULT true,
    bridge_status BOOLEAN DEFAULT false,
    blood_group VARCHAR(20) NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(15),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    donor_type VARCHAR(30) DEFAULT 'Regular Donor',
    last_contacted_date DATE,
    last_donation_date DATE,
    next_eligible_date DATE,
    donations_till_date INTEGER DEFAULT 0,
    eligibility_status VARCHAR(20) DEFAULT 'eligible',
    cycle_of_donations INTEGER DEFAULT 90,
    total_calls INTEGER DEFAULT 0,
    frequency_in_days INTEGER DEFAULT 0,
    status_of_bridge BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'active',
    donated_earlier BOOLEAN DEFAULT false,
    last_bridge_donation_date DATE,
    calls_to_donations_ratio DECIMAL(6,2) DEFAULT 0,
    user_donation_active_status VARCHAR(20) DEFAULT 'Active',
    inactive_trigger_comment TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PRAAN AI - Patients Table
-- Matches thalassemia_transfusion_10k.csv schema
-- 25 sample records based on dataset format
-- ============================================

-- Add missing columns to existing patients table
ALTER TABLE patients ADD COLUMN IF NOT EXISTS patient_code VARCHAR(20);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS sex VARCHAR(5);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS phone VARCHAR(15);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS weight_kg DECIMAL(5,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS spleen_enlargement VARCHAR(20);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS rdw_pct DECIMAL(5,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS hb_a_pct DECIMAL(5,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS mentzer_index DECIMAL(6,2);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS hb_post_transfusion DECIMAL(4,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS hb_drop_rate_per_day DECIMAL(6,4);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS hb_transfusion_threshold DECIMAL(4,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS days_since_last_transfusion INTEGER;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS units_per_session DECIMAL(3,1);
ALTER TABLE patients ADD COLUMN IF NOT EXISTS avg_transfusion_interval_days INTEGER;
ALTER TABLE patients ADD COLUMN IF NOT EXISTS days_until_next_transfusion INTEGER;

-- ============================================
-- INSERT DONORS (30 records)
-- Based on Dataset.md format, dates adjusted for 2026
-- ============================================

INSERT INTO donors (
    user_id, bridge_id, role, role_status, bridge_status,
    blood_group, gender, phone, latitude, longitude,
    donor_type, last_contacted_date, last_donation_date, next_eligible_date,
    donations_till_date, eligibility_status, cycle_of_donations,
    total_calls, frequency_in_days, status_of_bridge, status,
    donated_earlier, last_bridge_donation_date, calls_to_donations_ratio,
    user_donation_active_status, inactive_trigger_comment
) VALUES
-- Active Bridge Donors (high reliability, low ratio)
('D001', 'P001', 'Bridge Donor', true, true, 'O+', 'Male', '7671991949', 17.3850, 78.4867,
 'Regular Donor', '2026-05-20', '2026-05-15', '2026-08-13',
 8, 'eligible', 90, 9, 28, true, 'active',
 true, '2026-05-15', 1.13, 'Active', NULL),

('D002', 'P002', 'Bridge Donor', true, true, 'A+', 'Male', '9182234363', 17.3920, 78.4600,
 'Regular Donor', '2026-05-25', '2026-05-10', '2026-08-08',
 5, 'eligible', 90, 6, 22, true, 'active',
 true, '2026-05-10', 1.20, 'Active', NULL),

('D003', 'P003', 'Bridge Donor', true, true, 'B+', 'Female', '7671991949', 17.3880, 78.4750,
 'Regular Donor', '2026-05-18', '2026-04-28', '2026-07-27',
 12, 'eligible', 90, 14, 25, true, 'active',
 true, '2026-04-28', 1.17, 'Active', NULL),

('D004', 'P004', 'Bridge Donor', true, true, 'AB+', 'Male', '9182234363', 17.3950, 78.4520,
 'Regular Donor', '2026-05-22', '2026-05-20', '2026-08-18',
 3, 'eligible', 90, 4, 30, true, 'active',
 true, '2026-05-20', 1.33, 'Active', NULL),

('D005', 'P005', 'Bridge Donor', true, true, 'O-', 'Male', '7671991949', 17.3800, 78.4900,
 'Regular Donor', '2026-05-28', '2026-05-25', '2026-08-23',
 6, 'eligible', 90, 7, 20, true, 'active',
 true, '2026-05-25', 1.17, 'Active', NULL),

-- Active Emergency Donors (moderate reliability)
('D006', NULL, 'Emergency Donor', true, false, 'O+', 'Male', '9182234363', 17.4000, 78.4500,
 'Regular Donor', '2026-05-15', '2026-04-20', '2026-07-19',
 9, 'eligible', 90, 12, 18, false, 'active',
 true, NULL, 1.33, 'Active', NULL),

('D007', NULL, 'Emergency Donor', true, false, 'A+', 'Female', '7671991949', 17.3750, 78.4950,
 'Regular Donor', '2026-05-10', '2026-03-15', '2026-06-13',
 4, 'not eligible', 120, 8, 25, false, 'active',
 true, NULL, 2.00, 'Active', NULL),

('D008', NULL, 'Emergency Donor', true, false, 'B+', 'Male', '9182234363', 17.3900, 78.4700,
 'One-Time Donor', '2026-05-20', '2026-05-01', '2026-07-30',
 2, 'eligible', 90, 5, 15, false, 'active',
 true, NULL, 2.50, 'Active', NULL),

('D009', NULL, 'Emergency Donor', true, false, 'AB-', 'Male', '7671991949', 17.3820, 78.4800,
 'Regular Donor', '2026-05-25', '2026-02-10', '2026-05-11',
 7, 'not eligible', 90, 10, 22, false, 'active',
 true, NULL, 1.43, 'Inactive', 'Not donated in last 3 months'),

('D010', NULL, 'Emergency Donor', true, false, 'O+', 'Female', '9182234363', 17.3950, 78.4650,
 'Regular Donor', '2026-05-18', '2026-04-05', '2026-07-04',
 11, 'eligible', 90, 13, 20, false, 'active',
 true, NULL, 1.18, 'Active', NULL),

-- Bridge Donors with varying reliability
('D011', 'P006', 'Bridge Donor', true, true, 'A-', 'Male', '7671991949', 17.3870, 78.4820,
 'Regular Donor', '2026-05-12', '2026-03-20', '2026-06-18',
 15, 'not eligible', 90, 20, 28, true, 'active',
 true, '2026-03-20', 1.33, 'Active', NULL),

('D012', 'P007', 'Bridge Donor', true, true, 'B-', 'Female', '9182234363', 17.3910, 78.4580,
 'Regular Donor', '2026-05-08', '2026-04-12', '2026-07-11',
 6, 'eligible', 90, 8, 24, true, 'active',
 true, '2026-04-12', 1.33, 'Active', NULL),

('D013', 'P008', 'Bridge Donor', true, true, 'O+', 'Male', '7671991949', 17.3840, 78.4710,
 'Regular Donor', '2026-05-30', '2026-05-28', '2026-08-26',
 20, 'eligible', 90, 22, 26, true, 'active',
 true, '2026-05-28', 1.10, 'Active', NULL),

('D014', 'P009', 'Bridge Donor', true, true, 'AB+', 'Female', '9182234363', 17.3960, 78.4480,
 'Regular Donor', '2026-05-05', '2026-01-15', '2026-04-15',
 3, 'not eligible', 90, 6, 30, true, 'active',
 true, '2026-01-15', 2.00, 'Inactive', 'Not donated in last 4 months'),

('D015', 'P010', 'Bridge Donor', true, true, 'A+', 'Male', '7671991949', 17.3780, 78.4930,
 'Regular Donor', '2026-05-22', '2026-05-18', '2026-08-16',
 10, 'eligible', 90, 11, 21, true, 'active',
 true, '2026-05-18', 1.10, 'Active', NULL),

-- Emergency Donors (inactive - high ratio)
('D016', NULL, 'Emergency Donor', true, false, 'O+', 'Male', '9182234363', 17.4020, 78.4400,
 'One-Time Donor', '2026-04-10', '2025-08-14', '2025-11-12',
 1, 'not eligible', 90, 23, 0, false, 'active',
 true, NULL, 23.00, 'Inactive', 'Very limited activity despite multiple calls'),

('D017', NULL, 'Emergency Donor', true, false, 'A+', 'Male', '7671991949', 17.3700, 78.5000,
 'One-Time Donor', '2026-03-15', '2025-11-05', '2026-02-03',
 5, 'not eligible', 90, 4, 0, false, 'active',
 true, NULL, 0.80, 'Inactive', 'Not donated in last 6 months'),

('D018', NULL, 'Emergency Donor', true, false, 'B+', 'Female', '9182234363', 17.3850, 78.4600,
 'One-Time Donor', '2026-04-20', '2025-11-28', '2026-03-28',
 1, 'not eligible', 120, 15, 0, false, 'active',
 true, NULL, 15.00, 'Inactive', 'Very limited activity despite multiple calls'),

('D019', NULL, 'Emergency Donor', true, false, 'AB+', 'Male', '7671991949', 17.3920, 78.4750,
 'One-Time Donor', '2026-02-01', '2025-04-13', '2025-07-12',
 3, 'not eligible', 90, 12, 0, false, 'active',
 true, NULL, 4.00, 'Inactive', 'Very limited activity despite multiple calls'),

('D020', NULL, 'Emergency Donor', true, false, 'O+', 'Female', '9182234363', 17.3880, 78.4680,
 'One-Time Donor', '2026-01-15', '2025-12-23', '2026-04-22',
 3, 'not eligible', 120, 19, 0, false, 'active',
 true, NULL, 6.33, 'Inactive', 'Very limited activity despite multiple calls'),

-- More active donors
('D021', 'P011', 'Bridge Donor', true, true, 'O+', 'Male', '7671991949', 17.3860, 78.4850,
 'Regular Donor', '2026-05-28', '2026-05-22', '2026-08-20',
 14, 'eligible', 90, 15, 24, true, 'active',
 true, '2026-05-22', 1.07, 'Active', NULL),

('D022', 'P012', 'Bridge Donor', true, true, 'B+', 'Male', '9182234363', 17.3930, 78.4550,
 'Regular Donor', '2026-05-15', '2026-04-18', '2026-07-17',
 7, 'eligible', 90, 8, 26, true, 'active',
 true, '2026-04-18', 1.14, 'Active', NULL),

('D023', NULL, 'Emergency Donor', true, false, 'A+', 'Male', '7671991949', 17.3810, 78.4780,
 'Regular Donor', '2026-05-20', '2026-04-25', '2026-07-24',
 5, 'eligible', 90, 7, 22, false, 'active',
 true, NULL, 1.40, 'Active', NULL),

('D024', NULL, 'Emergency Donor', true, false, 'O-', 'Male', '9182234363', 17.3890, 78.4620,
 'Regular Donor', '2026-05-25', '2026-05-08', '2026-08-06',
 8, 'eligible', 90, 10, 19, false, 'active',
 true, NULL, 1.25, 'Active', NULL),

('D025', 'P013', 'Bridge Donor', true, true, 'AB-', 'Female', '7671991949', 17.3830, 78.4880,
 'Regular Donor', '2026-05-10', '2026-04-02', '2026-07-01',
 4, 'eligible', 90, 5, 28, true, 'active',
 true, '2026-04-02', 1.25, 'Active', NULL),

('D026', NULL, 'Emergency Donor', true, false, 'B-', 'Male', '9182234363', 17.3940, 78.4510,
 'Regular Donor', '2026-05-18', '2026-03-28', '2026-06-26',
 6, 'not eligible', 90, 9, 21, false, 'active',
 true, NULL, 1.50, 'Active', NULL),

('D027', 'P014', 'Bridge Donor', true, true, 'O+', 'Male', '7671991949', 17.3870, 78.4730,
 'Regular Donor', '2026-05-30', '2026-05-27', '2026-08-25',
 18, 'eligible', 90, 19, 23, true, 'active',
 true, '2026-05-27', 1.06, 'Active', NULL),

('D028', NULL, 'Emergency Donor', true, false, 'A+', 'Female', '7671991950', 17.3790, 78.4960,
 'Regular Donor', '2026-05-12', '2026-03-05', '2026-06-03',
 9, 'not eligible', 90, 14, 20, false, 'active',
 true, NULL, 1.56, 'Active', NULL),

('D029', NULL, 'Volunteer', true, false, 'O+', 'Male', '9182234365', 17.3850, 78.4700,
 'Regular Donor', '2026-05-08', '2026-04-15', '2026-07-14',
 6, 'eligible', 90, 4, 25, false, 'active',
 true, NULL, 0.67, 'Active', NULL),

('D030', 'P015', 'Bridge Donor', true, true, 'A+', 'Male', '7671991951', 17.3910, 78.4630,
 'Regular Donor', '2026-05-22', '2026-05-12', '2026-08-10',
 11, 'eligible', 90, 12, 22, true, 'active',
 true, '2026-05-12', 1.09, 'Active', NULL);

-- ============================================
-- INSERT PATIENTS (25 records)
-- Based on thalassemia_transfusion_10k.csv schema
-- ============================================

INSERT INTO patients (
    patient_code, name, age, sex, gender, weight_kg, blood_group, phone, location,
    spleen_enlargement, hb_level, rbc_count, mcv_level, mch_level, mchc_level,
    rdw_pct, ferritin_level, hb_a_pct, hb_a2, hb_f, mentzer_index,
    hb_post_transfusion, hb_drop_rate_per_day, hb_transfusion_threshold,
    days_since_last_transfusion, units_per_session, avg_transfusion_interval_days,
    days_until_next_transfusion, last_transfusion_date, transfusion_interval_days,
    severity, severity_score, urgency_level
) VALUES
-- Severe cases (Hb < 7, high HbF)
('THL-00001', 'Kavya Reddy', 8, 'F', 'Female', 22.5, 'O+', '7671991949', 'Hyderabad, Telangana',
 'Severe', 5.8, 3.20, 58.5, 16.8, 28.7,
 19.8, 2450, 4.2, 3.5, 92.3, 18.28,
 9.8, 0.14, 7.5,
 8, 3.0, 14, 6, '2026-05-30', 14,
 'Severe', 0.92, 'CRITICAL'),

('THL-00002', 'Rahul Kumar', 12, 'M', 'Male', 34.0, 'B+', '7671991949', 'Warangal, Telangana',
 'Moderate', 6.2, 3.50, 62.0, 17.5, 29.2,
 18.5, 1850, 6.8, 4.1, 89.1, 17.71,
 10.2, 0.12, 8.0,
 10, 4.0, 15, 5, '2026-05-28', 15,
 'Severe', 0.88, 'CRITICAL'),

('THL-00003', 'Ananya Sharma', 6, 'F', 'Female', 18.0, 'A+', '7671991949', 'Hyderabad, Telangana',
 'Severe', 5.5, 3.10, 56.0, 15.9, 28.4,
 20.2, 2680, 3.8, 3.2, 93.0, 18.06,
 9.5, 0.15, 7.0,
 7, 3.0, 14, 7, '2026-05-31', 14,
 'Severe', 0.90, 'CRITICAL'),

('THL-00004', 'Vikram Patel', 15, 'M', 'Male', 45.0, 'AB+', '7671991949', 'Secunderabad, Telangana',
 'Mild', 6.5, 3.60, 60.2, 17.0, 29.0,
 19.0, 1650, 8.5, 4.5, 87.0, 16.72,
 10.5, 0.11, 8.5,
 12, 4.0, 18, 6, '2026-05-26', 18,
 'Severe', 0.85, 'URGENT'),

('THL-00005', 'Priya Nair', 10, 'F', 'Female', 28.0, 'O-', '7671991949', 'Hyderabad, Telangana',
 'Moderate', 6.0, 3.35, 59.8, 16.5, 28.9,
 19.5, 2100, 5.5, 3.8, 90.7, 17.85,
 9.8, 0.13, 7.5,
 9, 3.0, 14, 5, '2026-05-29', 14,
 'Severe', 0.87, 'CRITICAL'),

-- Moderate-Severe cases
('THL-00006', 'Arjun Singh', 14, 'M', 'Male', 42.0, 'B+', '7671991949', 'Warangal, Telangana',
 'Moderate', 7.8, 4.10, 65.5, 18.2, 29.8,
 17.8, 850, 12.5, 4.8, 82.7, 15.98,
 10.8, 0.08, 8.0,
 18, 3.0, 21, 3, '2026-05-20', 21,
 'Moderate-Severe', 0.82, 'URGENT'),

('THL-00007', 'Sneha Gupta', 11, 'F', 'Female', 30.0, 'A+', '7671991949', 'Hyderabad, Telangana',
 'Mild', 8.0, 4.20, 66.0, 18.5, 30.0,
 17.5, 780, 14.0, 5.0, 81.0, 15.71,
 10.5, 0.07, 8.5,
 20, 3.0, 21, 1, '2026-05-18', 21,
 'Moderate-Severe', 0.80, 'SOON'),

('THL-00008', 'Rohan Das', 9, 'M', 'Male', 25.0, 'O+', '7671991949', 'Secunderabad, Telangana',
 'Moderate', 7.5, 4.00, 64.0, 17.8, 29.5,
 18.2, 920, 10.5, 4.2, 85.3, 16.00,
 10.2, 0.09, 7.5,
 15, 3.0, 18, 3, '2026-05-23', 18,
 'Moderate-Severe', 0.81, 'URGENT'),

('THL-00009', 'Ishita Menon', 13, 'F', 'Female', 38.0, 'AB-', '7671991949', 'Hyderabad, Telangana',
 'Moderate', 7.2, 3.85, 63.5, 17.5, 29.2,
 18.0, 980, 11.0, 4.5, 84.5, 16.49,
 10.0, 0.10, 8.0,
 16, 3.0, 21, 5, '2026-05-22', 21,
 'Moderate-Severe', 0.79, 'URGENT'),

('THL-00010', 'Aditya Joshi', 16, 'M', 'Male', 50.0, 'B-', '7671991949', 'Warangal, Telangana',
 'Mild', 8.2, 4.30, 67.0, 18.8, 30.2,
 17.2, 720, 15.0, 5.2, 79.8, 15.58,
 10.8, 0.06, 8.5,
 22, 4.0, 21, 0, '2026-05-16', 21,
 'Moderate-Severe', 0.78, 'SOON'),

-- Moderate cases
('THL-00011', 'Meera Iyer', 7, 'F', 'Female', 20.0, 'O+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 9.2, 4.80, 70.5, 19.5, 31.0,
 16.5, 420, 18.5, 5.5, 76.0, 14.69,
 10.5, 0.05, 9.0,
 25, 2.0, 28, 3, '2026-05-13', 28,
 'Moderate', 0.72, 'SOON'),

('THL-00012', 'Karthik Rao', 11, 'M', 'Male', 32.0, 'A+', '7671991949', 'Secunderabad, Telangana',
 'Normal', 9.5, 5.00, 71.0, 19.8, 31.2,
 16.2, 380, 20.0, 5.8, 74.2, 14.20,
 10.8, 0.04, 9.0,
 28, 3.0, 28, 0, '2026-05-10', 28,
 'Moderate', 0.70, 'SCHEDULED'),

('THL-00013', 'Divya Pillai', 9, 'F', 'Female', 24.0, 'B+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 8.8, 4.60, 69.0, 19.0, 30.5,
 17.0, 500, 16.0, 5.0, 79.0, 15.00,
 10.2, 0.06, 9.0,
 20, 2.0, 28, 8, '2026-05-18', 28,
 'Moderate', 0.71, 'SOON'),

('THL-00014', 'Suresh Babu', 14, 'M', 'Male', 44.0, 'AB+', '7671991949', 'Warangal, Telangana',
 'Normal', 9.8, 5.10, 72.0, 20.0, 31.5,
 15.8, 350, 22.0, 6.0, 72.0, 14.12,
 11.0, 0.04, 9.5,
 30, 3.0, 28, 0, '2026-05-08', 28,
 'Moderate', 0.68, 'SCHEDULED'),

('THL-00015', 'Lakshmi Devi', 8, 'F', 'Female', 22.0, 'O+', '7671991949', 'Hyderabad, Telangana',
 'Mild', 9.0, 4.70, 70.0, 19.2, 30.8,
 16.8, 450, 17.5, 5.2, 77.3, 14.89,
 10.5, 0.05, 9.0,
 22, 2.0, 28, 6, '2026-05-16', 28,
 'Moderate', 0.70, 'SOON'),

-- Mild cases
('THL-00016', 'Ganesh Kumar', 12, 'M', 'Male', 35.0, 'A+', '7671991949', 'Secunderabad, Telangana',
 'Normal', 11.2, 5.60, 74.0, 20.5, 32.0,
 15.0, 180, 28.0, 6.5, 65.5, 13.21,
 11.5, 0.03, 9.5,
 35, 2.0, 35, 0, '2026-05-03', 35,
 'Mild', 0.55, 'SCHEDULED'),

('THL-00017', 'Padma Lakshmi', 10, 'F', 'Female', 27.0, 'B+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 10.8, 5.40, 73.0, 20.2, 31.8,
 15.5, 210, 25.0, 6.2, 68.8, 13.52,
 11.2, 0.04, 9.5,
 30, 2.0, 28, 0, '2026-05-08', 28,
 'Mild', 0.52, 'SCHEDULED'),

('THL-00018', 'Rajesh Verma', 15, 'M', 'Male', 48.0, 'O+', '7671991949', 'Warangal, Telangana',
 'Normal', 12.0, 5.80, 75.0, 21.0, 32.5,
 14.8, 150, 30.0, 7.0, 63.0, 12.93,
 12.0, 0.02, 10.0,
 40, 3.0, 35, 0, '2026-04-28', 35,
 'Mild', 0.48, 'SCHEDULED'),

('THL-00019', 'Anjali Nair', 7, 'F', 'Female', 19.0, 'AB+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 11.5, 5.70, 74.5, 20.8, 32.2,
 15.2, 195, 27.0, 6.8, 66.2, 13.07,
 11.8, 0.03, 10.0,
 32, 2.0, 35, 3, '2026-05-06', 35,
 'Mild', 0.50, 'SCHEDULED'),

('THL-00020', 'Manoj Tiwari', 13, 'M', 'Male', 40.0, 'A-', '7671991949', 'Secunderabad, Telangana',
 'Normal', 10.5, 5.30, 72.5, 20.0, 31.5,
 15.8, 250, 24.0, 6.0, 70.0, 13.68,
 11.0, 0.04, 9.5,
 28, 3.0, 28, 0, '2026-05-10', 28,
 'Mild', 0.54, 'SCHEDULED'),

-- No Thalassemia (carrier/trait)
('THL-00021', 'Sanjay Reddy', 11, 'M', 'Male', 33.0, 'O+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 13.5, 6.20, 78.0, 22.0, 33.5,
 14.0, 95, 35.0, 4.8, 60.2, 12.58,
 NULL, NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL,
 'No Thalassemia', 0.15, 'SCHEDULED'),

('THL-00022', 'Rekha Sharma', 9, 'F', 'Female', 25.0, 'B+', '7671991949', 'Warangal, Telangana',
 'Normal', 13.0, 6.00, 77.0, 21.5, 33.0,
 14.2, 110, 33.0, 5.0, 62.0, 12.83,
 NULL, NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL,
 'No Thalassemia', 0.12, 'SCHEDULED'),

('THL-00023', 'Vijay Patel', 14, 'M', 'Male', 46.0, 'A+', '7671991949', 'Hyderabad, Telangana',
 'Normal', 14.0, 6.40, 79.0, 22.5, 34.0,
 13.8, 85, 36.0, 4.5, 59.5, 12.34,
 NULL, NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL,
 'No Thalassemia', 0.10, 'SCHEDULED'),

('THL-00024', 'Sunitha Rao', 8, 'F', 'Female', 21.0, 'AB+', '7671991949', 'Secunderabad, Telangana',
 'Normal', 12.8, 5.90, 76.5, 21.2, 32.8,
 14.5, 120, 32.0, 5.2, 62.8, 12.97,
 NULL, NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL,
 'No Thalassemia', 0.14, 'SCHEDULED'),

('THL-00025', 'Prakash Joshi', 12, 'M', 'Male', 36.0, 'O-', '7671991949', 'Hyderabad, Telangana',
 'Normal', 13.2, 6.10, 77.5, 21.8, 33.2,
 14.1, 100, 34.0, 4.9, 61.1, 12.70,
 NULL, NULL, NULL,
 NULL, NULL, NULL, NULL, NULL, NULL,
 'No Thalassemia', 0.13, 'SCHEDULED');

-- ============================================
-- INDEXES for performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_donors_blood_group ON donors(blood_group);
CREATE INDEX IF NOT EXISTS idx_donors_eligibility ON donors(eligibility_status);
CREATE INDEX IF NOT EXISTS idx_donors_active_status ON donors(user_donation_active_status);
CREATE INDEX IF NOT EXISTS idx_donors_role ON donors(role);
CREATE INDEX IF NOT EXISTS idx_donors_next_eligible ON donors(next_eligible_date);
CREATE INDEX IF NOT EXISTS idx_donors_latitude_longitude ON donors(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_patients_blood_group ON patients(blood_group);
CREATE INDEX IF NOT EXISTS idx_patients_severity ON patients(severity);
CREATE INDEX IF NOT EXISTS idx_patients_urgency ON patients(urgency_level);
CREATE INDEX IF NOT EXISTS idx_patients_code ON patients(patient_code);

-- ============================================
-- SUMMARY
-- ============================================
-- Donors: 30 records
--   - 15 Bridge Donors (linked to patients)
--   - 12 Emergency Donors
--   - 3 Inactive/One-Time Donors
--   - Blood groups: O+, O-, A+, A-, B+, B-, AB+, AB-
--
-- Patients: 25 records
--   - 5 Severe (Hb < 7, critical)
--   - 5 Moderate-Severe (Hb 7-8, urgent)
--   - 5 Moderate (Hb 8-10, soon)
--   - 5 Mild (Hb 10-12, scheduled)
--   - 5 No Thalassemia (carriers)
--   - All from Hyderabad/Warangal/Secunderabad region
-- ============================================
