-- Blood Banks table and data
CREATE TABLE IF NOT EXISTS blood_banks (
    bank_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(100),
    state VARCHAR(100),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blood inventory table (one row per blood group per bank)
CREATE TABLE IF NOT EXISTS blood_inventory (
    id SERIAL PRIMARY KEY,
    bank_id VARCHAR(10) REFERENCES blood_banks(bank_id),
    blood_group VARCHAR(5) NOT NULL,
    units_available INTEGER NOT NULL DEFAULT 0,
    expiry_date DATE,
    reserved_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(bank_id, blood_group)
);

-- Insert blood banks
INSERT INTO blood_banks (bank_id, name, district, state, contact_phone) VALUES
('bb001', 'Apollo Blood Bank', 'Hyderabad', 'Telangana', '+91 40-2345-6789'),
('bb002', 'NIMS Blood Centre', 'Hyderabad', 'Telangana', '+91 40-2348-9012'),
('bb003', 'Indian Red Cross Blood Bank', 'Secunderabad', 'Telangana', '+91 40-2789-0123'),
('bb004', 'Yashoda Blood Bank', 'Hyderabad', 'Telangana', '+91 40-4567-8901'),
('bb005', 'KIMS Blood Centre', 'Warangal', 'Telangana', '+91 870-234-5678'),
('bb006', 'Care Hospital Blood Bank', 'Hyderabad', 'Telangana', '+91 40-3456-7890'),
('bb007', 'Continental Blood Centre', 'Hyderabad', 'Telangana', '+91 40-6789-0123'),
('bb008', 'Rainbow Children Blood Bank', 'Hyderabad', 'Telangana', '+91 40-2345-0000'),
('bb009', 'MaxCure Blood Bank', 'Hyderabad', 'Telangana', '+91 40-2345-1111'),
('bb010', 'Global Hospitals Blood Bank', 'Hyderabad', 'Telangana', '+91 40-4477-8899'),
('bb011', 'Sunshine Blood Centre', 'Secunderabad', 'Telangana', '+91 40-2789-4455'),
('bb012', 'Omni Blood Bank', 'Warangal', 'Telangana', '+91 870-234-9900')
ON CONFLICT (bank_id) DO NOTHING;

-- Insert blood inventory
INSERT INTO blood_inventory (bank_id, blood_group, units_available, expiry_date, reserved_count) VALUES
('bb001', 'O+', 5, '2026-10-15', 1),
('bb001', 'A+', 3, '2026-09-28', 0),
('bb001', 'B+', 2, '2026-06-12', 0),

('bb002', 'B+', 4, '2026-09-20', 0),
('bb002', 'O-', 1, '2026-07-15', 0),
('bb002', 'A+', 2, '2026-08-30', 1),

('bb003', 'AB+', 2, '2026-10-02', 0),
('bb003', 'O+', 3, '2026-09-15', 0),

('bb004', 'A+', 6, '2026-10-20', 2),
('bb004', 'O+', 4, '2026-09-10', 0),
('bb004', 'B-', 1, '2026-06-09', 0),

('bb005', 'O+', 2, '2026-08-25', 0),
('bb005', 'B+', 3, '2026-09-05', 0),
('bb005', 'A-', 1, '2026-07-20', 0),

('bb006', 'O+', 7, '2026-11-01', 0),
('bb006', 'O-', 2, '2026-08-15', 1),
('bb006', 'AB+', 3, '2026-09-30', 0),

('bb007', 'B+', 5, '2026-10-10', 0),
('bb007', 'A+', 4, '2026-09-22', 0),
('bb007', 'AB-', 1, '2026-07-05', 0),

('bb008', 'O+', 3, '2026-08-18', 0),
('bb008', 'A+', 2, '2026-09-12', 0),
('bb008', 'B+', 1, '2026-06-15', 0),

('bb009', 'O+', 4, '2026-09-25', 0),
('bb009', 'A-', 2, '2026-08-10', 0),
('bb009', 'B+', 3, '2026-10-05', 1),

('bb010', 'O+', 6, '2026-10-30', 0),
('bb010', 'A+', 5, '2026-11-15', 0),
('bb010', 'B+', 4, '2026-09-18', 0),
('bb010', 'AB+', 2, '2026-08-22', 0),

('bb011', 'O-', 3, '2026-09-01', 0),
('bb011', 'B+', 2, '2026-08-14', 0),
('bb011', 'A+', 3, '2026-10-12', 0),

('bb012', 'O+', 3, '2026-07-30', 0),
('bb012', 'B+', 2, '2026-09-08', 0)
ON CONFLICT (bank_id, blood_group) DO UPDATE SET
    units_available = EXCLUDED.units_available,
    expiry_date = EXCLUDED.expiry_date,
    reserved_count = EXCLUDED.reserved_count,
    last_updated = CURRENT_TIMESTAMP;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_blood_inventory_bank ON blood_inventory(bank_id);
CREATE INDEX IF NOT EXISTS idx_blood_inventory_group ON blood_inventory(blood_group);
CREATE INDEX IF NOT EXISTS idx_blood_inventory_expiry ON blood_inventory(expiry_date);

-- View for easy querying of available blood
CREATE OR REPLACE VIEW blood_availability AS
SELECT
    bb.bank_id,
    bb.name AS bank_name,
    bb.district,
    bb.state,
    bb.contact_phone,
    bi.blood_group,
    bi.units_available,
    bi.expiry_date,
    bi.reserved_count,
    bi.last_updated
FROM blood_banks bb
JOIN blood_inventory bi ON bb.bank_id = bi.bank_id
WHERE bi.units_available > 0
ORDER BY bi.expiry_date ASC;
