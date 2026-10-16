-- ============================================================
-- Healthcare Record Management Using Blockchain
-- Database setup script
-- ============================================================
-- Run this once in MySQL to create the database and tables.
-- Command line example:
--   mysql -u root -p < database.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS healthcare_blockchain;
USE healthcare_blockchain;

-- ------------------------------------------------------------
-- users table
-- Stores login information for authorized staff (doctors/admin)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'doctor'
);

-- ------------------------------------------------------------
-- patients table
-- Stores the ACTUAL healthcare record (sensitive data lives here,
-- never on the blockchain).
-- record_hash = SHA-256 hash generated from record fields.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10),
    blood_group VARCHAR(5),
    disease VARCHAR(150),
    prescription VARCHAR(255),
    record_date DATE NOT NULL,
    record_hash VARCHAR(64)
);

-- ------------------------------------------------------------
-- blockchain_log table
-- Keeps an audit trail of every blockchain transaction and
-- verification check (Word Document Section 7.3 & Module 7).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS blockchain_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(20) NOT NULL,
    action VARCHAR(20) NOT NULL,        -- 'STORE' or 'VERIFY'
    record_hash VARCHAR(64) NOT NULL,
    tx_hash VARCHAR(80),
    result VARCHAR(20),                 -- 'Verified' / 'Modified' / 'Stored'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Authorized Doctor User
-- username: doctor1   password: password123
-- ------------------------------------------------------------
INSERT INTO users (username, password_hash, role)
VALUES ('doctor1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'doctor')
ON DUPLICATE KEY UPDATE username = username;

-- ------------------------------------------------------------
-- 25 Clinical Patient Records with SHA-256 Hashes
-- ------------------------------------------------------------
INSERT INTO patients (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash) VALUES
('P001', 'Aarav Patel', 34, 'Male', 'O+', 'Acute Viral Fever', 'Paracetamol 650mg TDS, Oral Rehydration Salts', '2024-05-10', '1bf2cf3f1fa69e0004fcf1df9df4ff8ae1fb97e289bfad18a666e133e9d89953'),
('P002', 'Priya Nair', 28, 'Female', 'A+', 'Acute Bronchitis', 'Amoxicillin 625mg BD, Levocetirizine 5mg HS', '2024-05-11', '8f8ce91079d8b1390494df9da0ebba3a3d2427a1f5ce0bba027b4093952ba5c3'),
('P003', 'Rajesh Gupta', 52, 'Male', 'B+', 'Essential Hypertension', 'Amlodipine 5mg OD, Telmisartan 40mg OD', '2024-05-12', '9eb16e6328328148b111514757c9c06509f6e12e2e7742cf63110902c5f11ea5'),
('P004', 'Sneha Sharma', 24, 'Female', 'AB+', 'Migraine with Aura', 'Sumatriptan 50mg SOS, Naproxen 250mg', '2024-05-14', '7f4b8cf61fbfd84f4fb3155f932822a107ef4f85e50529d20c5885c704eefeb4'),
('P005', 'Mohammed Khan', 41, 'Male', 'O-', 'Type 2 Diabetes Mellitus', 'Metformin 500mg BD, Glimepiride 1mg OD', '2024-05-15', 'cf2e3a89a0b943d09a89d0e125c1109f2b8bbcfbd06fecaa34b17bfb9a7c36a4'),
('P006', 'Ananya Desai', 30, 'Female', 'B-', 'Dengue Fever without Warning Signs', 'IV Normal Saline, Paracetamol 500mg, Platelet Monitoring', '2024-05-16', 'c0b898beabf58f4a1fa1871239922a6136a50e5095d3daae84d2f096238b15d6'),
('P007', 'Vikram Singh', 63, 'Male', 'A-', 'Bilateral Knee Osteoarthritis', 'Glucosamine Sulfate 1500mg, Paracetamol 650mg SOS', '2024-05-17', 'e1ad09c3093ca24d35e05c8a417ceca0704984ea0bc8c691f6305a4132ddaf20'),
('P008', 'Sunita Verma', 47, 'Female', 'O+', 'Primary Hypothyroidism', 'Levothyroxine 50mcg OD fasting', '2024-05-18', '51259e86744c86cbafc00aa16d3f273db06385cf61b36916c022718e00c3b860'),
('P009', 'Amit Joshi', 36, 'Male', 'AB-', 'Gastroesophageal Reflux Disease', 'Pantoprazole 40mg OD AC, Domperidone 10mg', '2024-05-19', '899ef87b322675d045d31fb8488e0b96aeecba7f09a562efad5680c6114eb3a4'),
('P010', 'Neha Kulkarni', 22, 'Female', 'A+', 'Moderate Bronchial Asthma', 'Budesonide + Formoterol Inhaler 2 puffs BD', '2024-05-20', '48aa2185cfd27e997f6fbc3bba8bf5443fa58a698889aa3eb8e77ce2ce3bbd0b'),
('P011', 'Arjun Reddy', 58, 'Male', 'B+', 'Coronary Artery Disease', 'Atorvastatin 20mg HS, Ecosprin 75mg OD', '2024-05-21', 'abf68686d0bf764f69adfa9b50e38a2e22c073df2674e54e4df95213d2899fa5'),
('P012', 'Kavita Iyer', 39, 'Female', 'O+', 'Allergic Rhinitis & Sinusitis', 'Montelukast 10mg + Levocetirizine 5mg HS, Fluticasone Spray', '2024-05-22', '319d675628b030ca0623a9d2012015fa57c8bfbc6489b02a281896791cae7978'),
('P013', 'Rohan Mehta', 19, 'Male', 'A+', 'Acute Viral Gastroenteritis', 'ORS Sachets, Zinc Sulfate 20mg OD, Probiotic capsule', '2024-05-23', 'fa108ffad73f13fb46eeb6f1faae303ea5625bf94685ffca5f7aa95804561ae3'),
('P014', 'Pooja Chawla', 45, 'Female', 'B+', 'Iron Deficiency Anemia', 'Ferrous Ascorbate 100mg + Folic Acid 1.5mg OD', '2024-05-24', '770984920c78a3c94d221bb5874c760da80ad0ef53f0b2401f802146f483c6b2'),
('P015', 'Suresh Yadav', 67, 'Male', 'O+', 'Chronic Kidney Disease Stage 2', 'Torsemide 10mg OD, Sodium bicarbonate 500mg BD', '2024-05-25', '716a1321d017b2b622eb1fcebc36ad2e77e0d378037198bbd7f27fbbf0ee3fa8'),
('P016', 'Deepa Rao', 33, 'Female', 'AB+', 'Acute Cystitis (UTI)', 'Nitrofurantoin 100mg BD for 7 days, Cranberry extract', '2024-05-26', '6b71f9cf72836248da937d377bcf7a64da252fa84b8f041ff3468579ca3328e4'),
('P017', 'Manoj Kumar', 50, 'Male', 'A-', 'Lumbar Disc Herniation (L4-L5)', 'Aceclofenac 100mg + Thiocolchicoside 4mg BD, Lumbar belt', '2024-05-27', '94ff2d25e01eb124c6eef40d4fbbcfbdaec8b2c5e5332f183709b1c28cffc71a'),
('P018', 'Shweta Patil', 29, 'Female', 'O+', 'Streptococcal Pharyngitis', 'Azithromycin 500mg OD for 3 days, Betadine gargle', '2024-05-28', 'b786b86cf5b61cbf55c65b169ea24d2fa7eaec1858c735d4fa58892f0fb853e8'),
('P019', 'Karthik Raman', 43, 'Male', 'B-', 'Peptic Ulcer Disease', 'Rabeprazole 20mg BD, Clarithromycin 500mg BD', '2024-05-29', 'a341e3092b6a83602fba7b700f735c023d8cff846b4329d4db5df0969d273760'),
('P020', 'Meera Nambiar', 61, 'Female', 'A+', 'Seropositive Rheumatoid Arthritis', 'Methotrexate 10mg weekly, Folic acid 5mg', '2024-05-30', '19ca56a347101869e5d4cb7fb8084a44fefb36879e95977ec3478cf3bfcf9698'),
('P021', 'Sanjay Mishra', 54, 'Male', 'O+', 'Generalized Anxiety Disorder', 'Escitalopram 10mg OD, Clonazepam 0.25mg SOS', '2024-05-31', '69d300eb0be2183c5005b871c53e414c77fcba90fa6ca6f9a0c20146059d6825'),
('P022', 'Ritu Agarwal', 37, 'Female', 'B+', 'Chronic Urticaria', 'Fexofenadine 180mg OD, Calamine lotion local application', '2024-06-01', '7dbf9640960ea515d666795f5ee49bf2c5b7cb856170ceb253b21855e9ea0162'),
('P023', 'Harish Pillai', 72, 'Male', 'AB+', 'Primary Open-Angle Glaucoma', 'Latanoprost Eye Drops 0.005% 1 drop both eyes HS', '2024-06-02', '458021d7237937965aaefae222dfc70685ad81f185cba7da63914948a3e7ef9e'),
('P024', 'Divya Saxena', 26, 'Female', 'A+', 'Atopic Eczema', 'Clobetasol Propionate 0.05% cream, Liquid paraffin moisturizer', '2024-06-03', '77e748fc8984920b7987a02dbaf5f0132b84293f9ef300e57209ff8ce04a6217'),
('P025', 'Alok Banerjee', 48, 'Male', 'O-', 'Plasmodium vivax Malaria', 'Artemether 80mg + Lumefantrine 480mg, Primaquine 15mg', '2024-06-04', 'a6d0cfa8e055f1376e1a494eb72f10b7a840e53a272dfa52f9c5750005a8f598')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ------------------------------------------------------------
-- Audit Trail Sample Transactions
-- ------------------------------------------------------------
INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result, created_at) VALUES
('P001', 'STORE', '1bf2cf3f1fa69e0004fcf1df9df4ff8ae1fb97e289bfad18a666e133e9d89953', '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b', 'Stored', '2024-05-10 10:30:00'),
('P002', 'STORE', '8f8ce91079d8b1390494df9da0ebba3a3d2427a1f5ce0bba027b4093952ba5c3', '0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b', 'Stored', '2024-05-11 11:15:00'),
('P003', 'STORE', '9eb16e6328328148b111514757c9c06509f6e12e2e7742cf63110902c5f11ea5', '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c', 'Stored', '2024-05-12 09:45:00'),
('P003', 'VERIFY', '9eb16e6328328148b111514757c9c06509f6e12e2e7742cf63110902c5f11ea5', NULL, 'Verified', '2024-05-12 14:20:00'),
('P004', 'STORE', '7f4b8cf61fbfd84f4fb3155f932822a107ef4f85e50529d20c5885c704eefeb4', '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d', 'Stored', '2024-05-14 12:00:00'),
('P005', 'STORE', 'cf2e3a89a0b943d09a89d0e125c1109f2b8bbcfbd06fecaa34b17bfb9a7c36a4', '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e', 'Stored', '2024-05-15 15:30:00'),
('P006', 'STORE', 'c0b898beabf58f4a1fa1871239922a6136a50e5095d3daae84d2f096238b15d6', '0x5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f', 'Stored', '2024-05-16 10:10:00'),
('P006', 'VERIFY', 'c0b898beabf58f4a1fa1871239922a6136a50e5095d3daae84d2f096238b15d6', NULL, 'Verified', '2024-05-16 16:45:00');
