<<<<<<< HEAD
# Healthcare Record Management Using Blockchain

Diploma mini project prototype. Stores patient records in MySQL and stores
a SHA-256 hash of each record on a local blockchain (Hardhat + Solidity
smart contract) so that modifications can be detected.

This matches the PPT / documentation:
MySQL → Flask → SHA-256 → Smart Contract → Blockchain, and verification
by re-hashing and comparing.

---

## 1. Architecture (simple explanation)

```
Patient Details
      |
      v
MySQL Database   <---- stores the ACTUAL patient data (sensitive)
      |
      v
Flask Backend (Python)
      |
      v
SHA-256 Hash Generation   <---- fingerprint of the record
      |
      v
Solidity Smart Contract  --->  Blockchain (Hardhat local network)
                                 stores ONLY: Patient ID + hash
```

Verification:
```
MySQL record --> generate hash again --> compare with hash on blockchain
Same hash  -> "Record Verified"
Diff hash  -> "Record Modified"
```

Key point for viva: **the blockchain never stores medical data**, only the
Patient ID and its SHA-256 hash. MySQL is the actual database; the
blockchain is a tamper-evident verification layer on top of it.

---

## 2. Folder structure

```
healthcare-blockchain/
│
├── app.py                     Flask backend (routes, logic)
├── blockchain_helper.py       Talks to the smart contract (web3.py)
├── requirements.txt
│
├── database/
│   └── database.sql           Creates DB + tables + demo login
│
├── templates/                 HTML pages (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── add_patient.html
│   ├── patients.html
│   └── verify.html
│
├── static/
│   ├── css/style.css
│   └── js/script.js
│
├── blockchain/                Hardhat project
│   ├── contracts/HealthcareRecord.sol
│   ├── scripts/deploy.js
│   ├── hardhat.config.js
│   ├── package.json
│   └── deployment.json        (created automatically after deploy)
│
└── README.md
```

---

## 3. Prerequisites

Install these once:

- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm) — needed for Hardhat
- **MySQL Server** (with a root user/password you know)
- VS Code (recommended, but any editor works)

---

## 4. Setup — step by step

### Step A: MySQL database

1. Open a terminal in the project folder.
2. Run the setup script:
   ```
   mysql -u root -p < database/database.sql
   ```
3. This creates the `healthcare_blockchain` database, the `users`,
   `patients` and `blockchain_log` tables, and one demo login:
   - username: `doctor1`
   - password: `password123`

### Step B: Python / Flask setup

1. (Recommended) create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Mac/Linux)
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Open `app.py` and edit the `DB_CONFIG` dictionary near the top with
   your real MySQL username/password.

### Step C: Hardhat / blockchain setup

1. Open a **new, separate terminal**, go into the `blockchain` folder:
   ```
   cd blockchain
   npm install
   ```
2. Start the local Hardhat blockchain (keep this terminal open — this
   is your "blockchain node" running on your own PC):
   ```
   npx hardhat node
   ```
   You will see 20 test accounts with fake ETH printed — this is
   normal, they are Hardhat's built-in test accounts.

3. Open **another new terminal** (keep the node running), go into the
   `blockchain` folder again, compile and deploy the smart contract:
   ```
   cd blockchain
   npx hardhat run scripts/deploy.js --network localhost
   ```
4. This prints the deployed contract address and creates
   `blockchain/deployment.json` — the Flask app reads this file to
   know how to talk to the contract. **You must redo this deploy step
   every time you restart `npx hardhat node`**, because the local
   blockchain resets when it's restarted.

### Step D: Run the Flask app

1. Back in your first terminal (project root, virtual environment
   active), run:
   ```
   python app.py
   ```
2. Open your browser at: `http://127.0.0.1:5000`
3. Log in with `doctor1` / `password123`.

You should now have **3 things running at once**:
1. `npx hardhat node` (the local blockchain)
2. Flask app (`python app.py`)
3. Your browser

---

## 5. Testing procedure

1. **Add a record**: Dashboard → "Add New Patient Record" → fill in
   Patient ID `P001`, name, age, etc., Disease = `Fever` → Save.
   - The record is saved in MySQL.
   - A SHA-256 hash is generated.
   - The hash is sent to the smart contract (you'll see a transaction
     hash confirmation message, and activity in the Hardhat node
     terminal).

2. **Verify (unchanged) record**: Go to Patients → click "Verify" next
   to `P001`.
   - The app regenerates the hash from MySQL and compares it with the
     blockchain hash.
   - Result should show **"Record Verified"**.

3. **Demonstrate modification detection**:
   - Go to "Add Record" again.
   - Enter the **same Patient ID** `P001`, but change Disease to
     `Malaria`.
   - Save. This updates MySQL AND stores a **new** hash on the
     blockchain for `P001` (this is expected — in this simple
     prototype, saving a record always re-syncs MySQL and the
     blockchain).

   To actually **see** a mismatch (the core demo), instead:
   - Add `P001` with Disease = `Fever` and let it store Hash A.
   - Directly edit the row in MySQL (e.g. via MySQL Workbench or the
     command line) and change only the `disease` column to `Malaria`,
     **without** going through the Add Record form (so the blockchain
     hash is NOT updated).
   - Now click "Verify" for `P001`.
   - The app recalculates the hash from the (now changed) MySQL row,
     compares it with the old hash still on the blockchain, and shows
     **"Record Modified"**.

   This is the cleanest way to demonstrate detection in your viva,
   because it mirrors real tampering: someone changed the database
   directly, bypassing the app.

---

## 6. File-by-file explanation (for viva)

- **`database/database.sql`** — creates MySQL tables. `patients` holds
  the real data. `blockchain_log` is just a local audit trail of
  blockchain transactions (not required for verification to work, but
  useful to show traceability).

- **`blockchain/contracts/HealthcareRecord.sol`** — the smart contract.
  Two simple functions: `storeHash` (write) and `getHash` (read). It
  never touches patient data directly, only Patient ID + hash strings.

- **`blockchain/hardhat.config.js`, `package.json`, `scripts/deploy.js`**
  — Hardhat is the local blockchain *development/testing* environment.
  `deploy.js` compiles and deploys the contract, then writes its
  address and ABI (interface description) to `deployment.json`.

- **`blockchain_helper.py`** — the only file that uses `web3.py`. It
  connects to the Hardhat node, signs a transaction with a test
  account to call `storeHash`, and calls `getHash` (a free, read-only
  call — no transaction needed for reading).

- **`app.py`** — the Flask backend:
  - `hash_password` — SHA-256 for login passwords.
  - `generate_record_hash` — builds one fixed-order string from the
    record fields and SHA-256-hashes it. Same input → same hash.
  - `/add_patient` — saves to MySQL, generates hash, calls
    `blockchain_helper.store_hash_on_blockchain`.
  - `/verify/<patient_id>` — re-generates the hash from the current
    MySQL row, calls `blockchain_helper.get_hash_from_blockchain`,
    compares them, shows Verified/Modified.

- **`templates/*.html`** — simple server-rendered pages (Flask +
  Jinja2), styled with `static/css/style.css`.

---

## 7. Important notes (also useful to say in viva)

- This is a **prototype**, not a production hospital system. It has no
  role-based access control, encryption at rest, or regulatory
  compliance features — these are listed as future scope.
- The blockchain **only proves that data hasn't changed since the hash
  was stored** — it does not prove the original data entered was
  medically correct.
- Hardhat is a **local development network**, not "the blockchain"
  itself — in a real deployment this would be a proper Ethereum-
  compatible network.
- No digital signatures are used — this project relies purely on
  SHA-256 hashing plus blockchain immutability for integrity checking,
  as described in the documentation.
=======
# healthcare-record-management-system-
blockchain mini project 
>>>>>>> d573ffc666ae3effaafa35f51b84bf66f08e94b8
