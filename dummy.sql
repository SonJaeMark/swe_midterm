-- =====================================================
-- DATA SEEDING SCRIPT
-- Inserts: 3 Doctors, 3 Staff Members, 2 Patients
-- Passwords stored in plain text to match existing logic
-- =====================================================

-- -----------------------------------------------------
-- 1. INSERT 3 DOCTORS
-- -----------------------------------------------------
-- Doctor 1
INSERT INTO users (username, email, password_hash, role) 
VALUES ('doctor1', 'doctor1@email.com', 'pass1234', 'DOCTOR');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Gregory', 'House', 'General Medicine', '+1 555-0101');

-- Doctor 2
INSERT INTO users (username, email, password_hash, role) 
VALUES ('doctor2', 'doctor2@email.com', 'pass1234', 'DOCTOR');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Meredith', 'Grey', 'Cardiology', '+1 555-0102');

-- Doctor 3
INSERT INTO users (username, email, password_hash, role) 
VALUES ('doctor3', 'doctor3@email.com', 'pass1234', 'DOCTOR');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Leonard', 'McCoy', 'Pediatrics', '+1 555-0103');

-- -----------------------------------------------------
-- 2. INSERT 3 STAFF MEMBERS
-- -----------------------------------------------------
-- Staff 1
INSERT INTO users (username, email, password_hash, role) 
VALUES ('staff1', 'staff1@email.com', 'pass1234', 'STAFF');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Pam', 'Beesly', 'Receptionist', '+1 555-0201');

-- Staff 2
INSERT INTO users (username, email, password_hash, role) 
VALUES ('staff2', 'staff2@email.com', 'pass1234', 'STAFF');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Triage', 'Desk', 'Triage Nurse', '+1 555-0202');

-- Staff 3
INSERT INTO users (username, email, password_hash, role) 
VALUES ('staff3', 'staff3@email.com', 'pass1234', 'STAFF');

INSERT INTO medical_staff (user_id, first_name, last_name, specialty, phone_number) 
VALUES (LAST_INSERT_ID(), 'Admin', 'User', 'Clinic Manager', '+1 555-0203');

-- -----------------------------------------------------
-- 3. INSERT 2 PATIENTS (USERS)
-- -----------------------------------------------------
-- Patient 1
INSERT INTO users (username, email, password_hash, role) 
VALUES ('patient1', 'patient1@email.com', 'pass1234', 'PATIENT');

INSERT INTO patients (user_id, first_name, last_name, phone_number, date_of_birth, address) 
VALUES (LAST_INSERT_ID(), 'John', 'Doe', '+1 555-0301', '1990-05-15', '123 Main Street, Cityville');

-- Patient 2
INSERT INTO users (username, email, password_hash, role) 
VALUES ('patient2', 'patient2@email.com', 'pass1234', 'PATIENT');

INSERT INTO patients (user_id, first_name, last_name, phone_number, date_of_birth, address) 
VALUES (LAST_INSERT_ID(), 'Jane', 'Smith', '+1 555-0302', '1995-08-22', '456 Oak Avenue, Townsville');