-- Create database and schema
CREATE OR REPLACE DATABASE healthcare_db;
CREATE OR REPLACE SCHEMA healthcare_db.clinic_schema;

USE DATABASE healthcare_db;
USE SCHEMA clinic_schema;

-- Create tables
CREATE OR REPLACE TABLE healthcare_db.clinic_schema.patients (
    patient_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    email VARCHAR(100),
    phone VARCHAR(20),
    ssn VARCHAR(12),
    street_address VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE healthcare_db.clinic_schema.appointments (
    appointment_id INT,
    patient_id INT,
    provider_name VARCHAR(100),
    appointment_date TIMESTAMP,
    visit_type VARCHAR(50),
    diagnosis_code VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE healthcare_db.clinic_schema.billing (
    billing_id INT,
    patient_id INT,
    appointment_id INT,
    charge_amount NUMBER(10,2),
    insurance_provider VARCHAR(100),
    member_id VARCHAR(50),
    payment_method VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample data
INSERT INTO healthcare_db.clinic_schema.patients
(patient_id, first_name, last_name, date_of_birth, email, phone, ssn, street_address, city, state, zip_code)
VALUES
(1, 'Ava', 'Johnson', '1987-04-12', 'ava.johnson@email.com', '555-111-2222', '123-45-6789', '101 Maple St', 'Arlington', 'VA', '22201'),
(2, 'Noah', 'Williams', '1992-08-23', 'noah.williams@email.com', '555-222-3333', '234-56-7890', '202 Oak Ave', 'Alexandria', 'VA', '22314'),
(3, 'Mia', 'Brown', '1979-11-05', 'mia.brown@email.com', '555-333-4444', '345-67-8901', '303 Pine Rd', 'Fairfax', 'VA', '22030'),
(4, 'Liam', 'Davis', '1984-02-19', 'liam.davis@email.com', '555-444-5555', '456-78-9012', '404 Elm Dr', 'Woodbridge', 'VA', '22191'),
(5, 'Sophia', 'Miller', '1995-06-30', 'sophia.miller@email.com', '555-555-6666', '567-89-0123', '505 Cedar Ln', 'Manassas', 'VA', '20110');

INSERT INTO healthcare_db.clinic_schema.appointments
(appointment_id, patient_id, provider_name, appointment_date, visit_type, diagnosis_code, status)
VALUES
(1001, 1, 'Dr. Patel', '2026-05-02 09:00:00', 'Primary Care', 'J01.90', 'Completed'),
(1002, 2, 'Dr. Chen', '2026-05-03 10:30:00', 'Dermatology', 'L20.9', 'Completed'),
(1003, 3, 'Dr. Smith', '2026-05-04 13:15:00', 'Cardiology', 'I10', 'Scheduled'),
(1004, 4, 'Dr. Patel', '2026-05-05 08:45:00', 'Follow-up', 'E11.9', 'Cancelled'),
(1005, 5, 'Dr. Lee', '2026-05-06 15:00:00', 'Pediatrics', 'Z00.129', 'Completed');

INSERT INTO healthcare_db.clinic_schema.billing
(billing_id, patient_id, appointment_id, charge_amount, insurance_provider, member_id, payment_method)
VALUES
(5001, 1, 1001, 145.00, 'Aetna', 'AET-10001', 'Credit Card'),
(5002, 2, 1002, 210.00, 'Blue Cross', 'BCBS-20002', 'HSA'),
(5003, 3, 1003, 320.00, 'UnitedHealthcare', 'UHC-30003', 'Debit Card'),
(5004, 4, 1004, 95.00, 'Cigna', 'CIG-40004', 'Credit Card'),
(5005, 5, 1005, 175.00, 'Aetna', 'AET-50005', 'Insurance');

-- Create role and grant permissions
CREATE OR REPLACE ROLE hc_analyst_demo;

GRANT USAGE ON DATABASE healthcare_db TO ROLE hc_analyst_demo;
GRANT USAGE ON SCHEMA healthcare_db.clinic_schema TO ROLE hc_analyst_demo;
GRANT SELECT ON ALL TABLES IN SCHEMA healthcare_db.clinic_schema TO ROLE hc_analyst_demo;

-- Create secure masked view
CREATE OR REPLACE SECURE VIEW clinic_schema.masked_patients AS
SELECT 
  patient_id,
  first_name,
  last_name,
  date_of_birth,
  CASE 
    WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN') THEN ssn
    WHEN CURRENT_ROLE() IN ('HC_ANALYST_DEMO') THEN '***-**-****'
  END AS ssn
FROM clinic_schema.patients;

-- Grant role to user and test
GRANT ROLE HC_ANALYST_DEMO TO USER <user_name>;

USE ROLE HC_ANALYST_DEMO;

SELECT role_name, patient_id, last_name, first_name, ssn
FROM clinic_schema.masked_patients;
