# app.py
# The main backend logic for the Fleet Management application.

import os
import csv
import io
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

@app.route('/admin/phone-numbers')
@login_required
@role_required('Administrator')
def admin_phone_numbers():
    """Serves the page for managing phone numbers."""
    return render_template('admin/phone_numbers.html')

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

@app.route('/admin/import')
@login_required
@role_required('Administrator')
def admin_import_csv():
    """Serves the CSV data import page."""
    return render_template('admin/import.html')

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

# --- CSV Import API Endpoint ---

@app.route('/api/admin/import_csv', methods=['POST'])
@login_required
@role_required('Administrator')
def import_csv():
    """API endpoint to handle CSV file upload and database processing."""
    
    # Check if file is present in request
    if 'csv_file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['csv_file']
    
    # Check if file has a name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Get target table name from form data
    target_table = request.form.get('target_table')
    
    # Whitelist of allowed target tables
    allowed_tables = ['phones', 'sim_cards', 'workers']
    if target_table not in allowed_tables:
        return jsonify({"error": "Invalid target table"}), 400
    
    try:
        # Read file content as string
        file_content = file.stream.read().decode("utf-8")
        
        # Parse CSV using DictReader
        csv_reader = csv.DictReader(io.StringIO(file_content))
        
        # Connect to database
        db = get_db()
        cursor = db.cursor()
        
        # Begin transaction
        row_count = 0
        
        # Process each row
        for row in csv_reader:
            # Filter out empty values and prepare data
            clean_row = {k: v for k, v in row.items() if v is not None and v.strip() != ''}
            
            if not clean_row:
                continue
                
            # Build upsert query based on target table
            if target_table == 'phones':
                # Primary unique key: asset_tag
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                # Build SET clause for ON CONFLICT DO UPDATE
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'asset_tag'])
                
                upsert_query = f"""
                    INSERT INTO phones ({column_names})
                    VALUES ({placeholders})
                    ON CONFLICT (asset_tag) DO UPDATE SET {set_clause}
                """
                
            elif target_table == 'sim_cards':
                # Primary unique key: iccid
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                # Build SET clause for ON CONFLICT DO UPDATE
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'iccid'])
                
                upsert_query = f"""
                    INSERT INTO sim_cards ({column_names})
                    VALUES ({placeholders})
                    ON CONFLICT (iccid) DO UPDATE SET {set_clause}
                """
                
            elif target_table == 'workers':
                # Primary unique key: worker_id
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                
                # Build SET clause for ON CONFLICT DO UPDATE
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'worker_id'])
                
                upsert_query = f"""
                    INSERT INTO workers ({column_names})
                    VALUES ({placeholders})
                    ON CONFLICT (worker_id) DO UPDATE SET {set_clause}
                """
            
            # Execute upsert statement
            cursor.execute(upsert_query, list(clean_row.values()))
            row_count += 1
        
        # Commit transaction
        db.commit()
        cursor.close()
        
        return jsonify({"message": f"Successfully processed {row_count} rows."}), 200
        
    except Exception as e:
        # Rollback transaction on error
        if 'db' in locals():
            db.rollback()
        if 'cursor' in locals():
            cursor.close()
        return jsonify({"error": "An error occurred during CSV processing.", "details": str(e)}), 500

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

# --- Phone Numbers Management ---

@app.route('/api/phone-numbers', methods=['GET', 'POST'])
@login_required
@role_required('Administrator')
def handle_phone_numbers():
    """API endpoint to get all phone numbers or create a new one."""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute("""
            SELECT 
                pn.id,
                pn.phone_number,
                pn.status,
                s.id as sim_id,
                s.iccid,
                s.carrier,
                CASE 
                    WHEN a.id IS NOT NULL THEN 'Assigned'
                    WHEN s.status = 'In Stock' THEN 'Available'
                    ELSE 'Unassigned'
                END as assignment_status,
                w.full_name as assigned_to_worker
            FROM phone_numbers pn
            LEFT JOIN sim_cards s ON pn.sim_card_id = s.id
            LEFT JOIN assignments a ON s.id = a.sim_card_id AND a.return_date IS NULL
            LEFT JOIN workers w ON a.worker_id = w.id
            ORDER BY pn.phone_number
        """)
        phone_numbers = cursor.fetchall()
        cursor.close()
        return jsonify(phone_numbers)
    
    elif request.method == 'POST':
        data = request.get_json()
        phone_number = data.get('phone_number')
        sim_card_id = data.get('sim_card_id')
        
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        try:
            cursor.execute(
                "INSERT INTO phone_numbers (phone_number, sim_card_id, status) VALUES (%s, %s, %s) RETURNING id;",
                (phone_number, sim_card_id, 'Active')
            )
            new_id = cursor.fetchone()['id']
            db.commit()
            
            # Fetch the complete record for response
            cursor.execute("""
                SELECT 
                    pn.id,
                    pn.phone_number,
                    pn.status,
                    s.id as sim_id,
                    s.iccid,
                    s.carrier
                FROM phone_numbers pn
                LEFT JOIN sim_cards s ON pn.sim_card_id = s.id
                WHERE pn.id = %s
            """, (new_id,))
            new_phone_number = cursor.fetchone()
            cursor.close()
            return jsonify(new_phone_number), 201
        except psycopg2.IntegrityError:
            db.rollback()
            cursor.close()
            return jsonify({"error": "This phone number already exists"}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/phone-numbers/<int:number_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@role_required('Administrator')
def handle_phone_number(number_id):
    """API endpoint to get, update, or delete a specific phone number."""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute("""
            SELECT 
                pn.id,
                pn.phone_number,
                pn.status,
                s.id as sim_id,
                s.iccid,
                s.carrier
            FROM phone_numbers pn
            LEFT JOIN sim_cards s ON pn.sim_card_id = s.id
            WHERE pn.id = %s
        """, (number_id,))
        phone_number = cursor.fetchone()
        cursor.close()
        return jsonify(phone_number) if phone_number else (jsonify({"error": "Phone number not found"}), 404)
    
    elif request.method == 'PUT':
        data = request.get_json()
        phone_number = data.get('phone_number')
        sim_card_id = data.get('sim_card_id')
        status = data.get('status')
        
        if not phone_number:
            return jsonify({"error": "Phone number is required"}), 400
        
        try:
            cursor.execute(
                "UPDATE phone_numbers SET phone_number = %s, sim_card_id = %s, status = %s WHERE id = %s",
                (phone_number, sim_card_id, status, number_id)
            )
            db.commit()
            
            # Fetch updated record
            cursor.execute("""
                SELECT 
                    pn.id,
                    pn.phone_number,
                    pn.status,
                    s.id as sim_id,
                    s.iccid,
                    s.carrier
                FROM phone_numbers pn
                LEFT JOIN sim_cards s ON pn.sim_card_id = s.id
                WHERE pn.id = %s
            """, (number_id,))
            updated_phone_number = cursor.fetchone()
            cursor.close()
            return jsonify(updated_phone_number)
        except psycopg2.IntegrityError:
            db.rollback()
            cursor.close()
            return jsonify({"error": "This phone number already exists"}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
    elif request.method == 'DELETE':
        cursor.execute("SELECT phone_number FROM phone_numbers WHERE id = %s", (number_id,))
        phone_number = cursor.fetchone()
        if not phone_number:
            return jsonify({"error": "Phone number not found"}), 404
        
        cursor.execute("UPDATE phone_numbers SET status = 'Inactive' WHERE id = %s", (number_id,))
        db.commit()
        cursor.close()
        return jsonify({"message": f"Phone number {phone_number['phone_number']} has been deactivated."})

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


@app.route('/admin/reports')
@login_required
@role_required('Administrator')
def admin_reports():
    """Serves the main reporting page for Administrators."""
    return render_template('admin/reports.html')


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


# --- API Endpoint for Admin Reports ---

@app.route('/api/reports/assignment_overview', methods=['GET'])
@login_required
@role_required('Administrator')
def get_assignment_overview():
    """
    Provides a comprehensive overview of all current assignments, joining
    workers, phones, SIMs, and phone numbers.
    """
    db = get_db()
    cursor = db.cursor()
    query = """
        SELECT 
            a.id AS assignment_id,
            w.full_name AS worker_name,
            w.worker_id,
            s.secteur_name,
            p.asset_tag,
            p.manufacturer,
            p.model,
            sc.iccid,
            pn.phone_number,
            a.assignment_date
        FROM assignments a
        JOIN workers w ON a.worker_id = w.id
        JOIN secteurs s ON w.secteur_id = s.id
        JOIN phones p ON a.phone_id = p.id
        JOIN sim_cards sc ON a.sim_card_id = sc.id
        LEFT JOIN phone_numbers pn ON sc.id = pn.sim_card_id
        WHERE a.return_date IS NULL
        ORDER BY s.secteur_name, w.full_name;
    """
    cursor.execute(query)
    report_data = cursor.fetchall()
    cursor.close()
    
    # Format dates for JSON
    for row in report_data:
        if row.get('assignment_date'):
            row['assignment_date'] = row['assignment_date'].isoformat()
            
    return jsonify(report_data)

# --- Enhanced Reports for Data Integrity ---

@app.route('/api/reports/missing_data', methods=['GET'])
@login_required
@role_required('Administrator')
def get_missing_data_report():
    """
    Comprehensive report to identify missing or incomplete data across the system.
    """
    db = get_db()
    cursor = db.cursor()
    
    report = {
        "sim_cards_without_phone_numbers": [],
        "phone_numbers_without_sim_cards": [],
        "sim_cards_without_assignments": [],
        "phones_without_assignments": [],
        "workers_without_assignments": [],
        "incomplete_phone_records": [],
        "incomplete_sim_records": [],
        "incomplete_worker_records": []
    }
    
    # SIM cards without phone numbers
    cursor.execute("""
        SELECT s.id, s.iccid, s.carrier, s.status
        FROM sim_cards s
        LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id
        WHERE pn.id IS NULL AND s.status != 'Deactivated'
        ORDER BY s.iccid
    """)
    report["sim_cards_without_phone_numbers"] = cursor.fetchall()
    
    # Phone numbers without SIM cards
    cursor.execute("""
        SELECT pn.id, pn.phone_number, pn.status
        FROM phone_numbers pn
        WHERE pn.sim_card_id IS NULL AND pn.status = 'Active'
        ORDER BY pn.phone_number
    """)
    report["phone_numbers_without_sim_cards"] = cursor.fetchall()
    
    # SIM cards without current assignments (available for deployment)
    cursor.execute("""
        SELECT s.id, s.iccid, s.carrier, pn.phone_number
        FROM sim_cards s
        LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id
        WHERE s.status = 'In Stock'
        AND s.id NOT IN (
            SELECT sim_card_id FROM assignments WHERE return_date IS NULL
        )
        ORDER BY s.carrier, pn.phone_number
    """)
    report["sim_cards_without_assignments"] = cursor.fetchall()
    
    # Phones without current assignments (available for deployment)
    cursor.execute("""
        SELECT p.id, p.asset_tag, p.manufacturer, p.model, p.status
        FROM phones p
        WHERE p.status = 'In Stock'
        AND p.id NOT IN (
            SELECT phone_id FROM assignments WHERE return_date IS NULL
        )
        ORDER BY p.asset_tag
    """)
    report["phones_without_assignments"] = cursor.fetchall()
    
    # Workers without current assignments (available for new assignments)
    cursor.execute("""
        SELECT w.id, w.worker_id, w.full_name, s.secteur_name
        FROM workers w
        JOIN secteurs s ON w.secteur_id = s.id
        WHERE w.status = 'Active'
        AND w.id NOT IN (
            SELECT worker_id FROM assignments WHERE return_date IS NULL
        )
        ORDER BY w.full_name
    """)
    report["workers_without_assignments"] = cursor.fetchall()
    
    # Incomplete phone records (missing key information)
    cursor.execute("""
        SELECT id, asset_tag, manufacturer, model, imei, serial_number, purchase_date, warranty_end_date
        FROM phones
        WHERE status != 'Retired' AND (
            manufacturer IS NULL OR manufacturer = '' OR
            model IS NULL OR model = '' OR
            imei IS NULL OR imei = '' OR
            serial_number IS NULL OR serial_number = '' OR
            purchase_date IS NULL OR
            warranty_end_date IS NULL
        )
        ORDER BY asset_tag
    """)
    report["incomplete_phone_records"] = cursor.fetchall()
    
    # Incomplete SIM records (missing key information)
    cursor.execute("""
        SELECT s.id, s.iccid, s.carrier, s.plan_details, pn.phone_number
        FROM sim_cards s
        LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id
        WHERE s.status != 'Deactivated' AND (
            s.carrier IS NULL OR s.carrier = '' OR
            s.plan_details IS NULL OR s.plan_details = ''
        )
        ORDER BY s.iccid
    """)
    report["incomplete_sim_records"] = cursor.fetchall()
    
    # Incomplete worker records (missing key information)
    cursor.execute("""
        SELECT w.id, w.worker_id, w.full_name, s.secteur_name
        FROM workers w
        JOIN secteurs s ON w.secteur_id = s.id
        WHERE w.status = 'Active' AND (
            w.full_name IS NULL OR w.full_name = '' OR
            w.secteur_id IS NULL
        )
        ORDER BY w.worker_id
    """)
    report["incomplete_worker_records"] = cursor.fetchall()
    
    cursor.close()
    
    # Format dates for JSON
    for category in report.values():
        for item in category:
            for key, value in item.items():
                if hasattr(value, 'isoformat'):
                    item[key] = value.isoformat()
    
    return jsonify(report)

@app.route('/api/reports/inventory_summary', methods=['GET'])
@login_required
@role_required('Administrator')
def get_inventory_summary():
    """
    Provides a comprehensive inventory summary with counts and availability.
    """
    db = get_db()
    cursor = db.cursor()
    
    summary = {}
    
    # Phone inventory summary
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            COUNT(CASE WHEN manufacturer IS NULL OR manufacturer = '' THEN 1 END) as missing_manufacturer,
            COUNT(CASE WHEN model IS NULL OR model = '' THEN 1 END) as missing_model,
            COUNT(CASE WHEN imei IS NULL OR imei = '' THEN 1 END) as missing_imei,
            COUNT(CASE WHEN purchase_date IS NULL THEN 1 END) as missing_purchase_date
        FROM phones
        WHERE status != 'Retired'
        GROUP BY status
        ORDER BY status
    """)
    summary["phones_by_status"] = cursor.fetchall()
    
    # SIM card inventory summary
    cursor.execute("""
        SELECT 
            s.status,
            COUNT(*) as count,
            COUNT(pn.id) as with_phone_numbers,
            COUNT(*) - COUNT(pn.id) as without_phone_numbers,
            COUNT(CASE WHEN s.carrier IS NULL OR s.carrier = '' THEN 1 END) as missing_carrier
        FROM sim_cards s
        LEFT JOIN phone_numbers pn ON s.id = pn.sim_card_id
        WHERE s.status != 'Deactivated'
        GROUP BY s.status
        ORDER BY s.status
    """)
    summary["sim_cards_by_status"] = cursor.fetchall()
    
    # Worker summary
    cursor.execute("""
        SELECT 
            w.status,
            COUNT(*) as count,
            COUNT(a.id) as with_assignments,
            COUNT(*) - COUNT(a.id) as without_assignments
        FROM workers w
        LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
        GROUP BY w.status
        ORDER BY w.status
    """)
    summary["workers_by_status"] = cursor.fetchall()
    
    # Phone numbers summary
    cursor.execute("""
        SELECT 
            pn.status,
            COUNT(*) as count,
            COUNT(s.id) as linked_to_sim,
            COUNT(*) - COUNT(s.id) as unlinked
        FROM phone_numbers pn
        LEFT JOIN sim_cards s ON pn.sim_card_id = s.id
        GROUP BY pn.status
        ORDER BY pn.status
    """)
    summary["phone_numbers_by_status"] = cursor.fetchall()
    
    cursor.close()
    return jsonify(summary)

# --- API Endpoints for Admin Dashboard Widgets ---

@app.route('/api/reports/summary_stats', methods=['GET'])
@login_required
@role_required('Administrator')
def get_summary_stats():
    """Provides key summary statistics for the admin dashboard."""
    db = get_db()
    cursor = db.cursor()
    
    queries = {
        "active_workers": "SELECT COUNT(*) FROM workers WHERE status = 'Active'",
        "phones_in_stock": "SELECT COUNT(*) FROM phones WHERE status = 'In Stock'",
        "phones_in_use": "SELECT COUNT(*) FROM phones WHERE status = 'In Use'",
        "open_tickets": "SELECT COUNT(*) FROM tickets WHERE status NOT IN ('Solved', 'Closed')"
    }
    
    stats = {}
    for key, query in queries.items():
        cursor.execute(query)
        stats[key] = cursor.fetchone()['count']
        
    cursor.close()
    return jsonify(stats)

@app.route('/api/reports/worker_assignments', methods=['GET'])
@login_required
@role_required('Administrator')
def get_worker_assignments():
    """
    Provides a list of all active workers and their currently assigned assets.
    """
    db = get_db()
    cursor = db.cursor()
    
    # Get all active workers first
    cursor.execute("SELECT id, full_name, worker_id, secteur_name FROM workers w JOIN secteurs s ON w.secteur_id = s.id WHERE w.status = 'Active' ORDER BY w.full_name")
    workers = cursor.fetchall()
    
    # Get all current assignments
    cursor.execute("""
        SELECT a.worker_id, p.asset_tag, p.model, sc.iccid, pn.phone_number
        FROM assignments a
        JOIN phones p ON a.phone_id = p.id
        JOIN sim_cards sc ON a.sim_card_id = sc.id
        LEFT JOIN phone_numbers pn ON sc.id = pn.sim_card_id
        WHERE a.return_date IS NULL
    """)
    assignments = cursor.fetchall()
    cursor.close()
    
    # Create a lookup map for assignments
    assignment_map = {a['worker_id']: a for a in assignments}
    
    # Combine the data
    result = []
    for worker in workers:
        worker_data = dict(worker)
        assignment_info = assignment_map.get(worker['id'])
        if assignment_info:
            worker_data['asset'] = {
                "phone_asset_tag": assignment_info['asset_tag'],
                "phone_model": assignment_info['model'],
                "sim_iccid": assignment_info['iccid'],
                "phone_number": assignment_info['phone_number']
            }
        else:
            worker_data['asset'] = None
        result.append(worker_data)
        
    return jsonify(result)

@app.route('/api/admin/assignments/<int:assignment_id>', methods=['DELETE'])
@login_required
@role_required('Administrator')
def return_assignment(assignment_id):
    """
    Handles the return of an asset from a worker.
    Sets the assignment's return_date, updates asset statuses, and logs the event.
    """
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Step 1: Find the assignment and the associated asset IDs
        cursor.execute("SELECT phone_id, sim_card_id, worker_id FROM assignments WHERE id = %s AND return_date IS NULL", (assignment_id,))
        assignment = cursor.fetchone()
        
        if not assignment:
            return jsonify({"error": "Active assignment not found."}), 404
            
        phone_id = assignment['phone_id']
        sim_id = assignment['sim_card_id']
        worker_id = assignment['worker_id']

        # Step 2: Update the assignment with a return date
        cursor.execute("UPDATE assignments SET return_date = now() WHERE id = %s", (assignment_id,))
        
        # Step 3: Update the status of the phone and SIM back to 'In Stock'
        cursor.execute("UPDATE phones SET status = 'In Stock' WHERE id = %s", (phone_id,))
        cursor.execute("UPDATE sim_cards SET status = 'In Stock' WHERE id = %s", (sim_id,))
        
        # Step 4: Log the return events
        log_event(cursor, 'Phone', phone_id, 'Returned', f"Asset returned from worker ID {worker_id}.")
        log_event(cursor, 'SIM', sim_id, 'Returned', f"SIM returned from worker ID {worker_id}.")
        
        db.commit()
        cursor.close()
        
        return jsonify({"message": "Asset successfully returned to inventory."})

    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({"error": "An error occurred during the return process.", "details": str(e)}), 500

# --- CSV Import Wizard Routes & API Endpoints ---

@app.route('/admin/import')
@login_required
@role_required('Administrator')
def admin_import():
    """Serves the CSV import wizard page."""
    return render_template('import.html')

@app.route('/api/import/preview', methods=['POST'])
@login_required
@role_required('Administrator')
def import_preview():
    """Handles CSV upload, reads headers and first 5 rows for preview."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400

    try:
        import csv
        import io

        # Read the file into memory
        file_content = file.stream.read().decode('utf-8')
        file.stream.seek(0) # Reset stream for full read later if needed

        # Use DictReader to get headers and preview data
        reader = csv.DictReader(io.StringIO(file_content))
        headers = reader.fieldnames
        
        preview_data = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            preview_data.append(row)

        # Get available table names from the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT tablename FROM pg_catalog.pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('phones', 'sim_cards', 'workers', 'users', 'secteurs', 'phone_numbers');
        """)
        tables = [row['tablename'] for row in cursor.fetchall()]
        cursor.close()

        return jsonify({
            "headers": headers,
            "preview_data": preview_data,
            "tables": tables
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route('/api/import/schema', methods=['POST'])
@login_required
@role_required('Administrator')
def import_get_schema():
    """Returns the column names and details for a given table."""
    data = request.get_json()
    table_name = data.get('table_name')
    
    # Security: Whitelist tables to prevent introspection of sensitive system tables
    allowed_tables = ['phones', 'sim_cards', 'workers', 'users', 'secteurs', 'phone_numbers']
    if not table_name or table_name not in allowed_tables:
        return jsonify({"error": "Invalid or unsupported table specified."}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns_info = []
        columns = []
        
        for row in cursor.fetchall():
            column_name = row['column_name']
            data_type = row['data_type']
            is_nullable = row['is_nullable'] == 'YES'
            column_default = row['column_default']
            max_length = row['character_maximum_length']
            
            # Format data type display
            type_display = data_type
            if max_length:
                type_display += f"({max_length})"
            
            # Check if it's a primary key or has constraints
            is_primary_key = False
            if column_default and 'nextval' in str(column_default):
                is_primary_key = True
            
            columns.append(column_name)
            columns_info.append({
                'name': column_name,
                'type': type_display,
                'nullable': is_nullable,
                'primary_key': is_primary_key,
                'default': column_default
            })
        
        cursor.close()
        return jsonify({
            "columns": columns,
            "columns_info": columns_info
        })
    except Exception as e:
        return jsonify({"error": f"Failed to fetch schema: {str(e)}"}), 500

@app.route('/api/import/process', methods=['POST'])
@login_required
@role_required('Administrator')
def import_process():
    """Processes the CSV data based on user-defined mappings."""
    data = request.get_json()
    
    # --- Data Validation ---
    required_keys = ['csv_data', 'target_table', 'merge_key_db', 'column_mappings']
    if not all(key in data for key in required_keys):
        return jsonify({"error": "Incomplete mapping data received."}), 400

    target_table = data['target_table']
    merge_key_db = data['merge_key_db']
    mappings = data['column_mappings']
    
    # Security: Whitelist tables again on the processing endpoint
    allowed_tables = ['phones', 'sim_cards', 'workers', 'users', 'secteurs', 'phone_numbers']
    if target_table not in allowed_tables:
        return jsonify({"error": "Invalid target table for import."}), 400

    if not mappings or not merge_key_db:
        return jsonify({"error": "A merge key and at least one mapped column are required."}), 400

    import csv
    import io
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        reader = csv.DictReader(io.StringIO(data['csv_data']))
        inserted_count = 0
        updated_count = 0

        for row in reader:
            # --- Dynamic SQL Generation (Safe with Parameterization) ---
            
            # Filter out the merge key from the update set
            update_mappings = {k: v for k, v in mappings.items() if v != merge_key_db}
            
            insert_cols = ", ".join(mappings.values())
            insert_placeholders = ", ".join(["%s"] * len(mappings))
            
            # Values for INSERT
            insert_values = [row.get(csv_col) for csv_col in mappings.keys()]
            
            # Build the query based on whether we have update mappings
            if update_mappings:
                # We have columns to update
                set_clause = ", ".join([f"{db_col} = %s" for db_col in update_mappings.values()])
                update_values = [row.get(csv_col) for csv_col in update_mappings.keys()]
                
                query = f"""
                    INSERT INTO {target_table} ({insert_cols})
                    VALUES ({insert_placeholders})
                    ON CONFLICT ({merge_key_db}) DO UPDATE
                    SET {set_clause}
                    RETURNING (xmax = 0) AS inserted;
                """
                
                # Combine all values for the final execution
                final_values = tuple(insert_values + update_values)
            else:
                # Only merge key, so just do INSERT ... ON CONFLICT DO NOTHING
                query = f"""
                    INSERT INTO {target_table} ({insert_cols})
                    VALUES ({insert_placeholders})
                    ON CONFLICT ({merge_key_db}) DO NOTHING;
                """
                
                final_values = tuple(insert_values)
            
            cursor.execute(query, final_values)
            
            # Handle result based on query type
            if update_mappings:
                result = cursor.fetchone()
                if result and (result[0] if isinstance(result, tuple) else result.get('inserted')):
                    inserted_count += 1
                else:
                    updated_count += 1
            else:
                # For DO NOTHING, we check if any row was affected
                if cursor.rowcount > 0:
                    inserted_count += 1
                # If no rows affected, it means the record already existed (conflict)

        db.commit()
        cursor.close()
        return jsonify({
            "message": "Import completed successfully!",
            "inserted": inserted_count,
            "updated": updated_count
        })

    except Exception as e:
        db.rollback()
        cursor.close()
        return jsonify({"error": f"An error occurred during import: {str(e)}"}), 500

@app.route('/api/phones/<int:phone_id>/history', methods=['GET'])
@login_required
@role_required('Administrator')
def get_phone_history(phone_id):
    """API endpoint to get the asset history log for a specific phone."""
    db = get_db()
    cursor = db.cursor()
    query = """
        SELECT 
            l.event_type,
            l.details,
            l.event_timestamp,
            u.full_name AS user_name
        FROM asset_history_log l
        LEFT JOIN users u ON l.user_id = u.id
        WHERE l.asset_type = 'Phone' AND l.asset_id = %s
        ORDER BY l.event_timestamp DESC;
    """
    cursor.execute(query, (phone_id,))
    history = cursor.fetchall()
    cursor.close()

    for item in history:
        if item.get('event_timestamp'):
            item['event_timestamp'] = item['event_timestamp'].isoformat()

    return jsonify(history)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
