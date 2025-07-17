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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
            # Return JSON error for API endpoints
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
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
        elif user['role_name'] == 'Support':
            return redirect(url_for('support_dashboard'))
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
    elif role == 'Support':
        return redirect(url_for('support_dashboard'))
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

@app.route('/admin/users')
@login_required
@role_required('Administrator')
def admin_users():
    """Serves the page for managing users."""
    return render_template('admin/users.html')

@app.route('/admin/roles')
@login_required
@role_required('Administrator')
def admin_roles():
    """Serves the page for managing roles."""
    return render_template('admin/roles.html')

@app.route('/admin/provision')
@login_required
@role_required('Administrator')
def admin_provision_wizard():
    """Serves the multi-step phone provisioning wizard page."""
    return render_template('admin/provision.html')

@app.route('/support/dashboard')
@login_required
@role_required('Support')
def support_dashboard():
    """Serves the main helpdesk dashboard for Support staff."""
    return render_template('support/dashboard.html')

# --- API Endpoints for Users and Roles ---
@app.route('/api/roles', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def manage_roles():
    """API endpoint to get all roles or create a new role."""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT id, role_name, description FROM roles ORDER BY role_name")
        roles = cursor.fetchall()
        cursor.close()
        return jsonify(roles)
    
    elif request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        role_name = data.get('role_name')
        description = data.get('description')
        
        if not role_name:
            return jsonify({'error': 'Role name is required'}), 400
        
        try:
            cursor.execute("""
                INSERT INTO roles (role_name, description) 
                VALUES (%s, %s) 
                RETURNING id, role_name, description
            """, (role_name, description))
            new_role = cursor.fetchone()
            db.commit()
            cursor.close()
            return jsonify(new_role), 201
        except psycopg2.IntegrityError as e:
            db.rollback()
            cursor.close()
            return jsonify({'error': 'Role name already exists'}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
@login_required
@role_required('Administrator')
def get_users():
    """API endpoint to get all users with role information."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.full_name, u.email, r.role_name
        FROM users u
        JOIN roles r ON u.role_id = r.id
        ORDER BY u.username
    """)
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
@login_required
@role_required('Administrator')
def create_user():
    """API endpoint to create a new user."""
    from werkzeug.security import generate_password_hash
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('role_id'):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        password_hash = generate_password_hash(data['password'])
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (data['username'], password_hash, data.get('full_name', ''), data.get('email', ''), data['role_id'])
        )
        new_user_id = cursor.fetchone()['id']
        db.commit()
        
        # Fetch the full new user data for the response
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.email, r.role_name
            FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = %s
        """, (new_user_id,))
        new_user = cursor.fetchone()
        cursor.close()
        return jsonify(new_user), 201
    except psycopg2.IntegrityError:
        db.rollback()
        return jsonify({"error": "A user with this username may already exist."}), 409
    except Exception as e:
        db.rollback()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('Administrator')
def update_user(user_id):
    """API endpoint to update an existing user."""
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    
    # Build update query dynamically based on provided fields
    update_fields = []
    values = []
    
    if 'full_name' in data:
        update_fields.append("full_name = %s")
        values.append(data['full_name'])
    if 'email' in data:
        update_fields.append("email = %s")
        values.append(data['email'])
    if 'role_id' in data:
        update_fields.append("role_id = %s")
        values.append(data['role_id'])
    
    if update_fields:
        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s", values)
        db.commit()
    
    cursor.execute("""
        SELECT u.id, u.username, u.full_name, u.email, r.role_name
        FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = %s
    """, (user_id,))
    updated_user = cursor.fetchone()
    cursor.close()
    return jsonify(updated_user)
    """API endpoint to get all roles or create a new one."""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT id, role_name, description FROM roles ORDER BY role_name")
        roles = cursor.fetchall()
        cursor.close()
        return jsonify(roles)
    
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('role_name'):
            return jsonify({"error": "Role name is required."}), 400
        
        try:
            cursor.execute(
                "INSERT INTO roles (role_name, description) VALUES (%s, %s) RETURNING *;",
                (data['role_name'], data.get('description', ''))
            )
            new_role = cursor.fetchone()
            db.commit()
            cursor.close()
            return jsonify(new_role), 201
        except psycopg2.IntegrityError:
            db.rollback()
            cursor.close()
            return jsonify({"error": "A role with this name already exists."}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@app.route('/api/roles/<int:role_id>', methods=['GET', 'PUT'])
@login_required
@role_required('Administrator')
def handle_role(role_id):
    """API endpoint to get or update a specific role."""
    db = get_db()
    cursor = db.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT id, role_name, description FROM roles WHERE id = %s", (role_id,))
        role = cursor.fetchone()
        cursor.close()
        if role:
            return jsonify(role)
        return jsonify({"error": "Role not found"}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if not data or not data.get('role_name'):
            return jsonify({"error": "Role name is required."}), 400
        
        role_name = data['role_name']
        description = data.get('description', '')
        
        try:
            cursor.execute(
                "UPDATE roles SET role_name = %s, description = %s WHERE id = %s RETURNING *;",
                (role_name, description, role_id)
            )
            updated_role = cursor.fetchone()
            if updated_role is None:
                db.rollback()
                cursor.close()
                return jsonify({"error": "Role not found."}), 404
            
            db.commit()
            cursor.close()
            return jsonify(updated_role)
        except psycopg2.IntegrityError as e:
            db.rollback()
            cursor.close()
            return jsonify({"error": "A role with this name already exists."}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

# --- New API Endpoints for Provisioning Wizard ---

@app.route('/api/provision/validate_phone', methods=['POST'])
@login_required
@role_required('Administrator')
def provision_validate_phone():
    """Validates that a phone exists and is in stock for provisioning."""
    data = request.get_json()
    identifier = data.get('identifier')
    if not identifier:
        return jsonify({"error": "Phone identifier (Asset Tag, IMEI, or Serial) is required."}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, asset_tag, manufacturer, model, status FROM phones WHERE asset_tag = %s OR imei = %s OR serial_number = %s",
        (identifier, identifier, identifier)
    )
    phone = cursor.fetchone()
    cursor.close()

    if not phone:
        return jsonify({"error": f"No phone found with identifier '{identifier}'."}), 404
    
    if phone['status'] != 'In Stock':
        return jsonify({"error": f"Phone {phone['asset_tag']} is currently '{phone['status']}' and cannot be provisioned."}), 409
        
    return jsonify(phone)


@app.route('/api/provision/available_assets', methods=['GET'])
@login_required
@role_required('Administrator')
def provision_get_available_assets():
    """Gets lists of available SIMs and Workers for assignment."""
    db = get_db()
    cursor = db.cursor()
    
    # Get SIMs in stock
    cursor.execute("SELECT s.id, s.iccid, s.carrier, pn.phone_number FROM sim_cards s LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id WHERE s.status = 'In Stock' ORDER BY s.carrier, pn.phone_number")
    sims = cursor.fetchall()

    # Get active workers not currently assigned a phone
    cursor.execute("""
        SELECT w.id, w.full_name, w.worker_id FROM workers w
        WHERE w.status = 'Active' AND w.id NOT IN (
            SELECT worker_id FROM assignments WHERE return_date IS NULL
        ) ORDER BY w.full_name
    """)
    workers = cursor.fetchall()
    
    cursor.close()
    return jsonify({"sims": sims, "workers": workers})


@app.route('/api/provision/finalize', methods=['POST'])
@login_required
@role_required('Administrator')
def provision_finalize():
    """Finalizes the provisioning process, creating the assignment and logs."""
    data = request.get_json()
    required_keys = ['phone_id', 'sim_id', 'worker_id']
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Missing data for finalization."}), 400

    phone_id = data['phone_id']
    sim_id = data['sim_id']
    worker_id = data['worker_id']
    user_id = session['user_id']

    db = get_db()
    cursor = db.cursor()

    try:
        # 1. Create the new assignment
        cursor.execute(
            "INSERT INTO assignments (phone_id, sim_card_id, worker_id, assignment_date) VALUES (%s, %s, %s, now())",
            (phone_id, sim_id, worker_id)
        )

        # 2. Update statuses
        cursor.execute("UPDATE phones SET status = 'In Use' WHERE id = %s", (phone_id,))
        cursor.execute("UPDATE sim_cards SET status = 'In Use' WHERE id = %s", (sim_id,))

        # 3. Create log entries
        log_event(cursor, 'Phone', phone_id, 'Provisioning Step', 'Physical inspection passed.')
        log_event(cursor, 'Phone', phone_id, 'Provisioning Step', 'Software configured.')
        log_event(cursor, 'Phone', phone_id, 'Assigned', f"Assigned to worker ID {worker_id}.")
        log_event(cursor, 'SIM', sim_id, 'Assigned', f"Assigned to worker ID {worker_id} with phone ID {phone_id}.")

        db.commit()
        cursor.close()
        return jsonify({"message": "Phone provisioned and assigned successfully!"})

    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({"error": "An error occurred during finalization.", "details": str(e)}), 500

@app.route('/manager/dashboard')
@login_required
@role_required('Manager')
def manager_dashboard():
    """Serves the main dashboard for Managers."""
    return render_template('manager/dashboard.html')

# --- API Endpoint for Manager Portal ---

@app.route('/api/manager/team_status', methods=['GET'])
@login_required
@role_required('Manager')
def get_manager_team_status():
    """
    API endpoint to get the status of all workers and their assigned assets
    for the currently logged-in manager.
    """
    manager_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()
    
    # This query securely fetches only the workers belonging to the manager's sectors.
    # It also gets details of their currently assigned phone and a count of any open tickets.
    query = """
        SELECT
            w.id AS worker_id,
            w.full_name AS worker_name,
            p.id AS phone_id,
            p.asset_tag,
            p.manufacturer,
            p.model,
            p.status AS phone_status,
            (SELECT COUNT(*)
             FROM tickets t
             WHERE t.phone_id = p.id AND t.status NOT IN ('Solved', 'Closed')) AS open_ticket_count
        FROM workers w
        LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
        LEFT JOIN phones p ON a.phone_id = p.id
        JOIN secteurs s ON w.secteur_id = s.id
        WHERE s.manager_id = %s
        ORDER BY w.full_name;
    """
    
    cursor.execute(query, (manager_id,))
    team_status = cursor.fetchall()
    cursor.close()
    
    return jsonify(team_status)

@app.route('/api/manager/selectable_phones', methods=['GET'])
@login_required
@role_required('Manager')
def get_manager_selectable_phones():
    """
    API endpoint to get all phones assigned to workers under the current manager,
    formatted for ticket creation dropdown.
    """
    manager_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()
    
    # Get all phones assigned to workers in the manager's sectors
    query = """
        SELECT
            p.id AS phone_id,
            w.full_name AS worker_name,
            p.asset_tag,
            p.manufacturer,
            p.model
        FROM phones p
        JOIN assignments a ON p.id = a.phone_id AND a.return_date IS NULL
        JOIN workers w ON a.worker_id = w.id
        JOIN secteurs s ON w.secteur_id = s.id
        WHERE s.manager_id = %s
        ORDER BY w.full_name;
    """
    
    cursor.execute(query, (manager_id,))
    selectable_phones = cursor.fetchall()
    cursor.close()
    
    return jsonify(selectable_phones)

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

# --- RESTful API Endpoints for Workers & Secteurs ---

@app.route('/api/secteurs', methods=['GET'])
@login_required
@role_required('Administrator')
def get_secteurs():
    """API endpoint to get a list of all secteurs."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, secteur_name FROM secteurs ORDER BY secteur_name")
    secteurs = cursor.fetchall()
    cursor.close()
    return jsonify(secteurs)

@app.route('/api/workers', methods=['GET'])
@login_required
@role_required('Administrator')
def get_workers():
    """API endpoint to get a list of all active workers with their sector name."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name
        FROM workers w
        JOIN secteurs s ON w.secteur_id = s.id
        WHERE w.status = 'Active'
        ORDER BY w.full_name
    """)
    workers = cursor.fetchall()
    cursor.close()
    return jsonify(workers)

@app.route('/api/workers', methods=['POST'])
@login_required
@role_required('Administrator')
def create_worker():
    """API endpoint to create a new worker."""
    data = request.get_json()
    if not data or not data.get('worker_id') or not data.get('full_name') or not data.get('secteur_id'):
        return jsonify({"error": "Missing required fields"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO workers (worker_id, full_name, secteur_id, status) VALUES (%s, %s, %s, 'Active') RETURNING id;",
            (data['worker_id'], data['full_name'], data['secteur_id'])
        )
        new_worker_id = cursor.fetchone()['id']
        db.commit()
        
        # Fetch the full new worker data for the response
        cursor.execute("""
            SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name
            FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.id = %s
        """, (new_worker_id,))
        new_worker = cursor.fetchone()
        cursor.close()
        return jsonify(new_worker), 201
    except psycopg2.IntegrityError:
        db.rollback()
        return jsonify({"error": "A worker with this Worker ID may already exist."}), 409
    except Exception as e:
        db.rollback()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@app.route('/api/workers/<int:worker_id>', methods=['PUT'])
@login_required
@role_required('Administrator')
def update_worker(worker_id):
    """API endpoint to update an existing worker."""
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE workers SET worker_id = %s, full_name = %s, secteur_id = %s WHERE id = %s;",
        (data['worker_id'], data['full_name'], data['secteur_id'], worker_id)
    )
    db.commit()
    
    cursor.execute("""
        SELECT w.id, w.worker_id, w.full_name, w.status, s.secteur_name
        FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.id = %s
    """, (worker_id,))
    updated_worker = cursor.fetchone()
    cursor.close()
    return jsonify(updated_worker)

@app.route('/api/workers/<int:worker_id>', methods=['DELETE'])
@login_required
@role_required('Administrator')
def delete_worker(worker_id):
    """API endpoint to 'delete' a worker by setting their status to 'Inactive'."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE workers SET status = 'Inactive' WHERE id = %s", (worker_id,))
    db.commit()
    cursor.close()
    return jsonify({"message": "Worker has been set to Inactive."}), 200

# --- API Endpoint for Support Portal ---

@app.route('/api/support/tickets', methods=['GET'])
@login_required
@role_required('Support')
def get_all_active_tickets():
    """
    API endpoint for Support to get all tickets that are not yet solved or closed.
    """
    db = get_db()
    cursor = db.cursor()
    
    # This query joins tickets with phones and the reporting manager's user table
    # to provide a comprehensive overview for the helpdesk.
    query = """
        SELECT 
            t.id AS ticket_id,
            t.title,
            t.status,
            t.priority,
            t.created_at,
            p.asset_tag AS phone_asset_tag,
            reporter.full_name AS reported_by,
            assignee.full_name AS assigned_to
        FROM tickets t
        JOIN phones p ON t.phone_id = p.id
        JOIN users reporter ON t.reported_by_manager_id = reporter.id
        LEFT JOIN users assignee ON t.assigned_to_support_id = assignee.id
        WHERE t.status NOT IN ('Solved', 'Closed')
        ORDER BY
            CASE t.priority
                WHEN 'Urgent' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                WHEN 'Low' THEN 4
            END,
            t.created_at ASC;
    """
    
    cursor.execute(query)
    tickets = cursor.fetchall()
    cursor.close()
    
    # Convert datetime objects to string format for JSON serialization
    for ticket in tickets:
        ticket['created_at'] = ticket['created_at'].isoformat()
        
    return jsonify(tickets)

# --- API Endpoint for Ticket Creation ---

@app.route('/api/tickets', methods=['POST'])
@login_required
@role_required('Manager')
def create_ticket():
    """
    API endpoint for Managers to create new support tickets.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['phone_id', 'title', 'description', 'priority']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate priority
        valid_priorities = ['Low', 'Medium', 'High', 'Urgent']
        if data['priority'] not in valid_priorities:
            return jsonify({'error': 'Invalid priority level'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify the phone exists and belongs to the manager's sector
        phone_check_query = """
            SELECT p.id, p.asset_tag, w.full_name as worker_name
            FROM phones p
            JOIN assignments a ON p.id = a.phone_id AND a.return_date IS NULL
            JOIN workers w ON a.worker_id = w.id
            JOIN secteurs s ON w.secteur_id = s.id
            WHERE p.id = %s AND s.manager_id = %s
        """
        cursor.execute(phone_check_query, (data['phone_id'], session.get('user_id')))
        phone_info = cursor.fetchone()
        
        if not phone_info:
            cursor.close()
            return jsonify({'error': 'Phone not found or not in your sector'}), 400
        
        # Insert the new ticket
        insert_query = """
            INSERT INTO tickets (title, description, phone_id, reported_by_manager_id, status, priority)
            VALUES (%s, %s, %s, %s, 'New', %s)
            RETURNING id
        """
        cursor.execute(insert_query, (
            data['title'],
            data['description'],
            data['phone_id'],
            session.get('user_id'),
            data['priority']
        ))
        
        ticket_id = cursor.fetchone()['id']
        db.commit()
        cursor.close()
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket_id': ticket_id,
            'phone_info': phone_info
        }), 201
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'error': f'Failed to create ticket: {str(e)}'}), 500

# --- New Route for Support Ticket Detail Page ---

@app.route('/support/ticket/<int:ticket_id>')
@login_required
@role_required('Support')
def support_ticket_detail(ticket_id):
    """Serves the detailed view page for a single support ticket."""
    return render_template('support/ticket_detail.html', ticket_id=ticket_id)


# --- New API Endpoints for a Single Ticket ---

@app.route('/api/support/ticket/<int:ticket_id>', methods=['GET'])
@login_required
@role_required('Support')
def get_ticket_details(ticket_id):
    """
    API endpoint to get all details for a single ticket, including phone,
    worker, and all historical updates.
    """
    db = get_db()
    cursor = db.cursor()
    
    # Main ticket details query
    ticket_query = """
        SELECT 
            t.*,
            p.asset_tag, p.manufacturer, p.model, p.serial_number,
            w.full_name AS worker_name,
            reporter.full_name AS reported_by,
            assignee.full_name AS assigned_to
        FROM tickets t
        JOIN phones p ON t.phone_id = p.id
        JOIN users reporter ON t.reported_by_manager_id = reporter.id
        LEFT JOIN users assignee ON t.assigned_to_support_id = assignee.id
        LEFT JOIN assignments a ON t.phone_id = a.phone_id AND a.return_date IS NULL
        LEFT JOIN workers w ON a.worker_id = w.id
        WHERE t.id = %s;
    """
    cursor.execute(ticket_query, (ticket_id,))
    ticket_details = cursor.fetchone()

    if not ticket_details:
        cursor.close()
        return jsonify({"error": "Ticket not found"}), 404

    # Updates query
    updates_query = """
        SELECT
            tu.id,
            tu.update_text,
            tu.created_at,
            tu.is_internal_note,
            u.full_name AS author_name
        FROM ticket_updates tu
        JOIN users u ON tu.update_author_id = u.id
        WHERE tu.ticket_id = %s
        ORDER BY tu.created_at ASC;
    """
    cursor.execute(updates_query, (ticket_id,))
    ticket_updates = cursor.fetchall()
    
    cursor.close()

    # Combine results and format dates for JSON
    ticket_details['updates'] = [dict(update) for update in ticket_updates]
    for key, value in ticket_details.items():
        if hasattr(value, 'isoformat'):
            ticket_details[key] = value.isoformat()
    for update in ticket_details['updates']:
        update['created_at'] = update['created_at'].isoformat()
            
    return jsonify(ticket_details)


@app.route('/api/support/ticket/<int:ticket_id>', methods=['PUT'])
@login_required
@role_required('Support')
def update_ticket_properties(ticket_id):
    """
    API endpoint for Support to update a ticket's core properties like
    status, priority, or assignment.
    """
    data = request.get_json()
    
    # Fields that a support agent is allowed to change
    allowed_fields = {
        'status': data.get('status'),
        'priority': data.get('priority'),
        'assigned_to_support_id': data.get('assigned_to_support_id')
    }
    
    # Filter out any fields not provided in the request
    update_data = {k: v for k, v in allowed_fields.items() if v is not None}
    
    if not update_data:
        return jsonify({"error": "No valid fields provided for update."}), 400

    # Build the SET part of the SQL query dynamically
    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(ticket_id)

    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(f"UPDATE tickets SET {set_clause} WHERE id = %s RETURNING id;", tuple(values))
        if cursor.fetchone() is None:
            return jsonify({"error": "Ticket not found"}), 404
        
        # Log this action
        log_details = f"Ticket properties updated: {', '.join(update_data.keys())}"
        log_event(cursor, 'Ticket', ticket_id, 'Properties Updated', log_details)
        
        db.commit()
        cursor.close()
        return jsonify({"message": "Ticket updated successfully."})
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500


@app.route('/api/support/ticket/<int:ticket_id>/updates', methods=['POST'])
@login_required
@role_required('Support')
def add_ticket_update(ticket_id):
    """
    API endpoint for Support to post a new update (comment) to a ticket.
    """
    data = request.get_json()
    if not data or not data.get('update_text'):
        return jsonify({"error": "Update text is required."}), 400

    user_id = session['user_id']
    update_text = data['update_text']
    is_internal = data.get('is_internal_note', False)

    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO ticket_updates (ticket_id, update_author_id, update_text, is_internal_note) VALUES (%s, %s, %s, %s) RETURNING id;",
            (ticket_id, user_id, update_text, is_internal)
        )
        db.commit()
        cursor.close()
        return jsonify({"message": "Update added successfully."}), 201
    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
