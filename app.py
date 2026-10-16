"""
app.py
======
Main Flask web application for:
"Healthcare Record Management Using Blockchain"

Main Modules (as defined in Documentation & Presentation):
1. Patient Management: Add, view, and manage patient records.
2. Authentication: Doctor / Admin secure login.
3. Medical Record Management: Disease, prescriptions, vitals.
4. Cryptographic Hashing: Deterministic SHA-256 fingerprint generation.
5. Blockchain Anchoring: Store record hash via Solidity smart contract (Remix IDE / Hardhat).
6. Record Verification: Re-calculate hash and compare with blockchain hash to detect tampering.
7. Audit Trail / Traceability: Transparent ledger of all operations.
8. Viva Tamper Simulator: Direct simulation of database tampering to demonstrate detection live.
"""

import hashlib
import os
import sqlite3
from datetime import datetime, date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import blockchain_helper

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "healthcare-blockchain-secret-2024")

# ------------------------------------------------------------
# Database Configuration (MySQL with automatic SQLite fallback)
# ------------------------------------------------------------
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Set your MySQL root password if running MySQL
    "database": "healthcare_blockchain",
    "connection_timeout": 2,
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "database", "healthcare_local.db")
USE_SQLITE = False


def hash_password(plain_password: str) -> str:
    """SHA-256 password hashing."""
    return hashlib.sha256(plain_password.encode()).hexdigest()


def generate_record_hash(patient_id, name, age, gender, blood_group, disease, prescription, record_date):
    """
    Standardized cryptographic fingerprint of the clinical record.
    Matches the exact formula specified in the PPT and documentation:
    record_string = patient_id|name|age|gender|blood_group|disease|prescription|record_date
    """
    record_string = f"{patient_id}|{name}|{age}|{gender}|{blood_group}|{disease}|{prescription}|{record_date}"
    return hashlib.sha256(record_string.encode()).hexdigest()


def init_sqlite_db():
    """Initializes local SQLite database if MySQL is not available."""
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'doctor'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT,
        blood_group TEXT,
        disease TEXT,
        prescription TEXT,
        record_date TEXT NOT NULL,
        record_hash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blockchain_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id TEXT NOT NULL,
        action TEXT NOT NULL,
        record_hash TEXT NOT NULL,
        tx_hash TEXT,
        result TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Demo user: doctor1 / password123
    default_pass_hash = hash_password("password123")
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, username, password_hash, role)
    VALUES (1, 'doctor1', ?, 'doctor')
    """, (default_pass_hash,))

    # Insert sample patient if table is empty
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        sample_hash = generate_record_hash(
            "P001", "Rahul Sharma", 34, "Male", "O+", "Fever", "Paracetamol 500mg", "2024-05-10"
        )
        cursor.execute("""
        INSERT INTO patients (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash)
        VALUES ('P001', 'Rahul Sharma', 34, 'Male', 'O+', 'Fever', 'Paracetamol 500mg', '2024-05-10', ?)
        """, (sample_hash,))

        cursor.execute("""
        INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result, created_at)
        VALUES ('P001', 'STORE', ?, '0x5c7b39...sample', 'Stored', datetime('now'))
        """, (sample_hash,))

    conn.commit()
    conn.close()


def get_db_connection():
    """Returns MySQL connection, or falls back to SQLite seamlessly."""
    global USE_SQLITE
    if not USE_SQLITE:
        try:
            import mysql.connector
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn, "mysql"
        except Exception:
            USE_SQLITE = True
            init_sqlite_db()

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


# Initialize SQLite backup database on app load
init_sqlite_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ================================================================
# ROUTES
# ================================================================

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn, db_type = get_db_connection()
        if db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            user = dict(row) if row else None

        conn.close()

        if user and user["password_hash"] == hash_password(password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user.get("role", "doctor")
            flash(f"Welcome back, Dr. {user['username']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Use demo: doctor1 / password123", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn, db_type = get_db_connection()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM patients")
        total_patients = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM blockchain_log WHERE action = 'VERIFY'")
        total_verifications = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM blockchain_log WHERE action = 'STORE'")
        total_anchors = cursor.fetchone()["total"]
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blockchain_log WHERE action = 'VERIFY'")
        total_verifications = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blockchain_log WHERE action = 'STORE'")
        total_anchors = cursor.fetchone()[0]

    conn.close()

    # Check blockchain connection
    bc_connected, bc_info = blockchain_helper.is_blockchain_connected()

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        total_patients=total_patients,
        total_verifications=total_verifications,
        total_anchors=total_anchors,
        bc_connected=bc_connected,
        bc_info=bc_info,
        db_type=db_type.upper(),
    )


@app.route("/add_patient", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        patient_id = request.form["patient_id"].strip().upper()
        name = request.form["name"].strip()
        age = int(request.form["age"].strip())
        gender = request.form.get("gender", "Other")
        blood_group = request.form.get("blood_group", "").strip().upper()
        disease = request.form["disease"].strip()
        prescription = request.form.get("prescription", "").strip()
        record_date = date.today().isoformat()

        # Step 1: Generate SHA-256 cryptographic fingerprint
        record_hash = generate_record_hash(
            patient_id, name, age, gender, blood_group, disease, prescription, record_date
        )

        # Step 2: Anchor hash to Blockchain (Smart Contract)
        tx_hash = None
        log_result = "Stored"
        try:
            tx_hash = blockchain_helper.store_hash_on_blockchain(patient_id, record_hash)
            bc_message = f"Record successfully anchored to Blockchain (Tx: {tx_hash[:16]}...)"
            flash(bc_message, "success")
        except Exception as e:
            # Fallback simulated anchor for demo if blockchain node is not active
            tx_hash = "0x" + hashlib.sha256(f"{patient_id}{record_hash}".encode()).hexdigest()[:40]
            log_result = f"Stored (Simulated: {e})"
            flash(f"Record saved. Smart contract notice: {e}", "warning")

        # Step 3: Save actual medical data in Database
        conn, db_type = get_db_connection()
        if db_type == "mysql":
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO patients
                   (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                     name=%s, age=%s, gender=%s, blood_group=%s, disease=%s,
                     prescription=%s, record_date=%s, record_hash=%s""",
                (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash,
                 name, age, gender, blood_group, disease, prescription, record_date, record_hash),
            )
            cursor.execute(
                """INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result)
                   VALUES (%s, 'STORE', %s, %s, %s)""",
                (patient_id, record_hash, tx_hash, log_result),
            )
            conn.commit()
            cursor.close()
        else:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO patients
                   (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(patient_id) DO UPDATE SET
                     name=excluded.name, age=excluded.age, gender=excluded.gender,
                     blood_group=excluded.blood_group, disease=excluded.disease,
                     prescription=excluded.prescription, record_date=excluded.record_date,
                     record_hash=excluded.record_hash""",
                (patient_id, name, age, gender, blood_group, disease, prescription, record_date, record_hash),
            )
            cursor.execute(
                """INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result)
                   VALUES (?, 'STORE', ?, ?, ?)""",
                (patient_id, record_hash, tx_hash, log_result),
            )
            conn.commit()

        conn.close()
        return redirect(url_for("patients"))

    return render_template("add_patient.html")


@app.route("/patients")
@login_required
def patients():
    conn, db_type = get_db_connection()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients ORDER BY record_date DESC")
        all_patients = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY record_date DESC")
        all_patients = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template("patients.html", patients=all_patients)


@app.route("/verify/<patient_id>")
@login_required
def verify(patient_id):
    conn, db_type = get_db_connection()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        record = cursor.fetchone()
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        record = dict(row) if row else None

    if not record:
        conn.close()
        flash("Patient record not found.", "error")
        return redirect(url_for("patients"))

    # Step 1: Re-hash CURRENT medical data from database
    current_hash = generate_record_hash(
        record["patient_id"], record["name"], record["age"], record["gender"],
        record["blood_group"], record["disease"], record["prescription"],
        record["record_date"],
    )

    # Step 2: Fetch ORIGINAL immutable hash from Blockchain
    blockchain_hash = None
    blockchain_details = None
    error = None

    try:
        blockchain_hash = blockchain_helper.get_hash_from_blockchain(patient_id)
        blockchain_details = blockchain_helper.get_record_details_from_blockchain(patient_id)
    except Exception as e:
        error = str(e)
        # Fallback to last stored hash in log table for verification demonstration
        if db_type == "mysql":
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT record_hash FROM blockchain_log WHERE patient_id = %s AND action = 'STORE' ORDER BY id DESC LIMIT 1",
                (patient_id,)
            )
            log_row = cursor.fetchone()
            cursor.close()
        else:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT record_hash FROM blockchain_log WHERE patient_id = ? AND action = 'STORE' ORDER BY id DESC LIMIT 1",
                (patient_id,)
            )
            log_row = cursor.fetchone()
        if log_row:
            blockchain_hash = log_row["record_hash"] if db_type == "mysql" else log_row[0]

    # Step 3: Core Verification Comparison Logic
    if error and not blockchain_hash:
        result = "Error"
    elif blockchain_hash is None:
        result = "No blockchain record found"
    elif current_hash == blockchain_hash:
        result = "Verified"
    else:
        result = "Modified"

    # Step 4: Record this verification attempt in the audit trail
    if db_type == "mysql":
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result)
               VALUES (%s, 'VERIFY', %s, NULL, %s)""",
            (patient_id, current_hash, result),
        )
        conn.commit()
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO blockchain_log (patient_id, action, record_hash, tx_hash, result)
               VALUES (?, 'VERIFY', ?, NULL, ?)""",
            (patient_id, current_hash, result),
        )
        conn.commit()

    conn.close()

    # Format timestamp if available
    block_timestamp = None
    recorded_by = None
    if blockchain_details and blockchain_details.get("timestamp"):
        try:
            block_timestamp = datetime.fromtimestamp(blockchain_details["timestamp"]).strftime("%Y-%m-%d %H:%M:%S UTC")
            recorded_by = blockchain_details.get("recorded_by")
        except Exception:
            pass

    return render_template(
        "verify.html",
        record=record,
        current_hash=current_hash,
        blockchain_hash=blockchain_hash,
        result=result,
        error=error,
        block_timestamp=block_timestamp,
        recorded_by=recorded_by,
    )


# ================================================================
# VIVA DEMONSTRATION TOOL: DIRECT DB TAMPER SIMULATOR
# ================================================================

@app.route("/tamper/<patient_id>", methods=["GET", "POST"])
@login_required
def tamper_record(patient_id):
    """
    Directly modifies the MySQL/SQLite database row WITHOUT updating
    the blockchain. This allows easy live demonstration of tamper detection
    during viva (Slide 5 of the presentation).
    """
    conn, db_type = get_db_connection()

    if request.method == "POST":
        new_disease = request.form.get("disease", "").strip()
        new_prescription = request.form.get("prescription", "").strip()

        if db_type == "mysql":
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE patients SET disease = %s, prescription = %s WHERE patient_id = %s",
                (new_disease, new_prescription, patient_id)
            )
            conn.commit()
            cursor.close()
        else:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE patients SET disease = ?, prescription = ? WHERE patient_id = ?",
                (new_disease, new_prescription, patient_id)
            )
            conn.commit()

        conn.close()
        flash(
            f"Tamper Simulated! Patient {patient_id} modified in database ONLY (Blockchain hash remains unchanged). Click 'Verify' to test detection!",
            "warning"
        )
        return redirect(url_for("verify", patient_id=patient_id))

    # GET: show tamper form
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        record = cursor.fetchone()
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        record = dict(row) if row else None

    conn.close()
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("patients"))

    return render_template("tamper.html", record=record)


# ================================================================
# AUDIT LOG / TRACEABILITY (Module 7 from Documentation)
# ================================================================

@app.route("/audit_log")
@login_required
def audit_log():
    conn, db_type = get_db_connection()
    if db_type == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM blockchain_log ORDER BY id DESC LIMIT 50")
        logs = cursor.fetchall()
        cursor.close()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_log ORDER BY id DESC LIMIT 50")
        logs = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template("audit_log.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
