# app.py
# The main backend logic for the Fleet Management application.

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from functools import wraps
from werkzeug.security import check_password_hash
from flask import (
    Flask, request, jsonify, render_template, session, redirect, url_for, g
)

# --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# --- Database Connection ---
def get_db():
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(os.environ.get('DATABASE_URL'), cursor_factory=RealDictCursor)
        except psycopg2.OperationalError as e:
            raise ConnectionError(f"Could not connect to the database: {e}")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Helper function for logging ---
def log_event(cursor, asset_type, asset_id, event_type, details):
    cursor.execute(
        "INSERT INTO asset_history_log (asset_type, asset_id, event_type, user_id, details) VALUES (%s, %s, %s, %s, %s)",
        (asset_type, asset_id, event_type, session.get('user_id'), details)
    )

# --- Authentication & Authorization Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != required_role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Main Application Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT u.id, u.username, u.password_hash, r.role_name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user is None or not check_password_hash(user['password_hash'], password):
            error = 'Incorrect username or password.'
            return render_template('login.html', error=error)
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role_name']
        if user['role_name'] == 'Administrator':
            return redirect(url_for('admin_dashboard'))
        elif user['role_name'] == 'Manager':
            return redirect(url_for('manager_dashboard'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    role = session.get('role')
    if role == 'Administrator':
        return redirect(url_for('admin_dashboard'))
    elif role == 'Manager':
        return redirect(url_for('manager_dashboard'))
    return redirect(url_for('logout'))

# --- Role-Specific Dashboards & Pages ---
@app.route('/admin/dashboard')
@login_required
@role_required('Administrator')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/phones')
@login_required
@role_required('Administrator')
def admin_phones():
    return render_template('admin/phones.html')

@app.route('/admin/sims')
@login_required
@role_required('Administrator')
def admin_sims():
    return render_template('admin/sims.html')

@app.route('/admin/workers')
@login_required
@role_required('Administrator')
def admin_workers():
    """Serves the page for managing workers."""
    return render_template('admin/workers.html')

@app.route('/manager/dashboard')
@login_required
@role_required('Manager')
def manager_dashboard():
    return f"<h1>Manager Dashboard for {session['username']}</h1><a href='/logout'>Logout</a>"

# --- API Endpoints ---

# PHONES
@app.route('/api/phones', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def handle_phones():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM phones WHERE status != 'Retired' ORDER BY id")
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    if request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute("INSERT INTO phones (asset_tag, imei, serial_number, manufacturer, model, purchase_date, warranty_end_date, status, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", (data['asset_tag'], data['imei'], data['serial_number'], data.get('manufacturer'), data.get('model'), data.get('purchase_date') or None, data.get('warranty_end_date') or None, data.get('status', 'In Stock'), data.get('notes')))
            new_id = cursor.fetchone()['id']
            log_event(cursor, 'Phone', new_id, 'Created', f"Phone asset {data['asset_tag']} created.")
            db.commit()
            cursor.execute("SELECT * FROM phones WHERE id = %s", (new_id,))
            new_item = cursor.fetchone()
            cursor.close()
            return jsonify(new_item), 201
        except psycopg2.IntegrityError:
            db.rollback()
            return jsonify({"error": "A phone with the same Asset Tag, IMEI, or Serial Number may already exist."}), 409

@app.route('/api/phones/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@role_required('Administrator')
def handle_phone(item_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM phones WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        return jsonify(item) if item else (jsonify({"error": "Not Found"}), 404)
    if request.method == 'PUT':
        data = request.get_json()
        cursor.execute("UPDATE phones SET asset_tag = %s, imei = %s, serial_number = %s, manufacturer = %s, model = %s, purchase_date = %s, warranty_end_date = %s, status = %s, notes = %s WHERE id = %s;", (data['asset_tag'], data['imei'], data['serial_number'], data.get('manufacturer'), data.get('model'), data.get('purchase_date') or None, data.get('warranty_end_date') or None, data.get('status'), data.get('notes'), item_id))
        log_event(cursor, 'Phone', item_id, 'Updated', f"Details for asset {data['asset_tag']} updated.")
        db.commit()
        cursor.execute("SELECT * FROM phones WHERE id = %s", (item_id,))
        updated_item = cursor.fetchone()
        cursor.close()
        return jsonify(updated_item)
    if request.method == 'DELETE':
        cursor.execute("SELECT asset_tag FROM phones WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item: return jsonify({"error": "Not Found"}), 404
        cursor.execute("UPDATE phones SET status = 'Retired' WHERE id = %s", (item_id,))
        log_event(cursor, 'Phone', item_id, 'Retired', f"Asset {item['asset_tag']} was retired.")
        db.commit()
        cursor.close()
        return jsonify({"message": f"Phone {item['asset_tag']} has been retired."})

# SIMS
@app.route('/api/sims', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def handle_sims():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT s.*, pn.phone_number FROM sim_cards s LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id WHERE s.status != 'Deactivated' ORDER BY s.id")
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    if request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute("INSERT INTO sim_cards (iccid, carrier, plan_details, status) VALUES (%s, %s, %s, %s) RETURNING id;", (data['iccid'], data.get('carrier'), data.get('plan_details'), data.get('status', 'In Stock')))
            new_id = cursor.fetchone()['id']
            if data.get('phone_number'):
                cursor.execute("INSERT INTO phone_numbers (phone_number, sim_card_id, status) VALUES (%s, %s, 'Active') ON CONFLICT (phone_number) DO UPDATE SET sim_card_id = %s;", (data['phone_number'], new_id, new_id))
            log_event(cursor, 'SIM', new_id, 'Created', f"SIM card {data['iccid']} created.")
            db.commit()
            cursor.execute("SELECT s.*, pn.phone_number FROM sim_cards s LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id WHERE s.id = %s", (new_id,))
            new_item = cursor.fetchone()
            cursor.close()
            return jsonify(new_item), 201
        except psycopg2.IntegrityError:
            db.rollback()
            return jsonify({"error": "A SIM with this ICCID may already exist."}), 409

@app.route('/api/sims/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@role_required('Administrator')
def handle_sim(item_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT s.*, pn.phone_number FROM sim_cards s LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id WHERE s.id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        return jsonify(item) if item else (jsonify({"error": "Not Found"}), 404)
    if request.method == 'PUT':
        data = request.get_json()
        cursor.execute("UPDATE sim_cards SET iccid = %s, carrier = %s, plan_details = %s, status = %s WHERE id = %s;", (data['iccid'], data.get('carrier'), data.get('plan_details'), data.get('status'), item_id))
        if data.get('phone_number'):
            cursor.execute("INSERT INTO phone_numbers (phone_number, sim_card_id, status) VALUES (%s, %s, 'Active') ON CONFLICT (phone_number) DO UPDATE SET sim_card_id = %s;", (data['phone_number'], item_id, item_id))
        log_event(cursor, 'SIM', item_id, 'Updated', f"Details for SIM {data['iccid']} updated.")
        db.commit()
        cursor.execute("SELECT s.*, pn.phone_number FROM sim_cards s LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id WHERE s.id = %s", (item_id,))
        updated_item = cursor.fetchone()
        cursor.close()
        return jsonify(updated_item)
    if request.method == 'DELETE':
        cursor.execute("SELECT iccid FROM sim_cards WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item: return jsonify({"error": "Not Found"}), 404
        cursor.execute("UPDATE sim_cards SET status = 'Deactivated' WHERE id = %s", (item_id,))
        cursor.execute("UPDATE phone_numbers SET status = 'Inactive' WHERE sim_card_id = %s", (item_id,))
        log_event(cursor, 'SIM', item_id, 'Deactivated', f"SIM {item['iccid']} was deactivated.")
        db.commit()
        cursor.close()
        return jsonify({"message": f"SIM {item['iccid']} has been deactivated."})

# WORKERS & SECTEURS
@app.route('/api/secteurs', methods=['GET'])
@login_required
@role_required('Administrator')
def get_secteurs():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, secteur_name FROM secteurs ORDER BY secteur_name")
    secteurs = cursor.fetchall()
    cursor.close()
    return jsonify(secteurs)

@app.route('/api/workers', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def handle_workers():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.status = 'Active' ORDER BY w.full_name")
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    if request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute("INSERT INTO workers (worker_id, full_name, secteur_id, status) VALUES (%s, %s, %s, 'Active') RETURNING id;", (data['worker_id'], data['full_name'], data['secteur_id']))
            new_id = cursor.fetchone()['id']
            db.commit()
            cursor.execute("SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.id = %s", (new_id,))
            new_item = cursor.fetchone()
            cursor.close()
            return jsonify(new_item), 201
        except psycopg2.IntegrityError:
            db.rollback()
            return jsonify({"error": "A worker with this Worker ID may already exist."}), 409

@app.route('/api/workers/<int:item_id>', methods=['PUT', 'DELETE'])
@login_required
@role_required('Administrator')
def handle_worker(item_id):
    db = get_db()
    cursor = db.cursor()
    if request.method == 'PUT':
        data = request.get_json()
        cursor.execute("UPDATE workers SET worker_id = %s, full_name = %s, secteur_id = %s WHERE id = %s;", (data['worker_id'], data['full_name'], data['secteur_id'], item_id))
        db.commit()
        cursor.execute("SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.id = %s", (item_id,))
        updated_item = cursor.fetchone()
        cursor.close()
        return jsonify(updated_item)
    if request.method == 'DELETE':
        cursor.execute("UPDATE workers SET status = 'Inactive' WHERE id = %s", (item_id,))
        db.commit()
        cursor.close()
        return jsonify({"message": "Worker has been set to Inactive."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
