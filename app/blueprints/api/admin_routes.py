# app/blueprints/api/admin_routes.py
# Admin API routes.

from flask import request, jsonify, current_app, session
from . import api_bp
from app.utils.decorators import login_required, role_required
from app.utils.helpers import get_db
import psycopg2

@api_bp.route('/roles', methods=['GET', 'POST'])
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
            current_app.logger.info("Role created successfully: %s by user %s", role_name, session.get('username'))
            return jsonify(new_role), 201
        except psycopg2.IntegrityError as e:
            db.rollback()
            cursor.close()
            current_app.logger.warning("Failed to create role %s - integrity error: %s", role_name, e)
            return jsonify({'error': 'Role name already exists'}), 409
        except Exception as e:
            db.rollback()
            cursor.close()
            current_app.logger.error("Unexpected error creating role %s: %s", role_name, e, exc_info=True)
            return jsonify({'error': str(e)}), 500

# NEW! Endpoint to fetch all sectors for filtering.
@api_bp.route('/sectors', methods=['GET'])
@login_required
def get_all_sectors():
    """API endpoint to get a list of all sectors."""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, secteur_name AS name FROM secteurs ORDER BY name")
        sectors = cursor.fetchall()
        cursor.close()
        return jsonify(sectors)
    except Exception as e:
        current_app.logger.error("Failed to fetch sectors: %s", e, exc_info=True)
        return jsonify({"error": "Failed to retrieve sectors"}), 500

@api_bp.route('/users', methods=['GET'])
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

@api_bp.route('/users', methods=['POST'])
@login_required
@role_required('Administrator')
def create_user():
    """API endpoint to create a new user."""
    from werkzeug.security import generate_password_hash
    from flask import session
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('role_id'):
        current_app.logger.warning("User creation attempt with missing fields by %s", session.get('username'))
        return jsonify({"error": "Missing required fields"}), 400

    username = data['username']
    current_app.logger.info("Creating user %s by administrator %s", username, session.get('username'))

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
        
        cursor.execute("""
            SELECT u.id, u.username, u.full_name, u.email, r.role_name
            FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = %s
        """, (new_user_id,))
        new_user = cursor.fetchone()
        cursor.close()
        
        current_app.logger.info("User %s created successfully with ID %s by %s", username, new_user_id, session.get('username'))
        return jsonify(new_user), 201
    except psycopg2.IntegrityError as e:
        db.rollback()
        cursor.close()
        current_app.logger.warning("Failed to create user %s - integrity constraint: %s", username, e)
        return jsonify({"error": "A user with this username may already exist."}), 409
    except Exception as e:
        db.rollback()
        cursor.close()
        current_app.logger.error("Unexpected error creating user %s: %s", username, e, exc_info=True)
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('Administrator')
def update_user(user_id):
    """API endpoint to update an existing user."""
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    
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

@api_bp.route('/roles/<int:role_id>', methods=['GET', 'PUT'])
@login_required
@role_required('Administrator')
def manage_role(role_id):
    """API endpoint to get or update a specific role."""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'GET':
        cursor.execute("SELECT id, role_name, description FROM roles WHERE id = %s", (role_id,))
        role = cursor.fetchone()
        cursor.close()
        if role:
            return jsonify(role)
        else:
            return jsonify({"error": "Role not found"}), 404
            
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        update_fields = []
        values = []
        
        if 'role_name' in data:
            update_fields.append("role_name = %s")
            values.append(data['role_name'])
        if 'description' in data:
            update_fields.append("description = %s")
            values.append(data['description'])
        
        if update_fields:
            values.append(role_id)
            try:
                cursor.execute(f"UPDATE roles SET {', '.join(update_fields)} WHERE id = %s", values)
                db.commit()
                
                cursor.execute("SELECT id, role_name, description FROM roles WHERE id = %s", (role_id,))
                updated_role = cursor.fetchone()
                cursor.close()
                return jsonify(updated_role)
            except psycopg2.IntegrityError as e:
                db.rollback()
                cursor.close()
                return jsonify({"error": "Role name already exists"}), 409
            except Exception as e:
                db.rollback()
                cursor.close()
                return jsonify({"error": str(e)}), 500
        else:
            cursor.close()
            return jsonify({"error": "No fields to update"}), 400

@api_bp.route('/admin/import_csv', methods=['POST'])
@login_required
@role_required('Administrator')
def import_csv():
    """API endpoint to handle CSV file upload and database processing."""
    import csv
    import io
    
    if 'csv_file' not in request.files:
        current_app.logger.warning("CSV import attempt without file by user %s", session.get('username'))
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['csv_file']
    
    if file.filename == '':
        current_app.logger.warning("CSV import attempt with empty filename by user %s", session.get('username'))
        return jsonify({"error": "No selected file"}), 400
    
    target_table = request.form.get('target_table')
    
    allowed_tables = ['phones', 'sim_cards', 'workers']
    if target_table not in allowed_tables:
        current_app.logger.warning("CSV import attempt with invalid table '%s' by user %s", target_table, session.get('username'))
        return jsonify({"error": "Invalid target table"}), 400
    
    current_app.logger.info("Starting CSV import for table '%s' from file '%s' by user %s", 
                   target_table, file.filename, session.get('username'))
    
    try:
        file_content = file.stream.read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(file_content))
        db = get_db()
        cursor = db.cursor()
        
        row_count = 0
        
        for row in csv_reader:
            clean_row = {k: v for k, v in row.items() if v is not None and v.strip() != ''}
            if not clean_row:
                continue
            
            if target_table == 'phones':
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'asset_tag'])
                upsert_query = f"""
                    INSERT INTO phones ({column_names}) VALUES ({placeholders})
                    ON CONFLICT (asset_tag) DO UPDATE SET {set_clause}
                """
            elif target_table == 'sim_cards':
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'iccid'])
                upsert_query = f"""
                    INSERT INTO sim_cards ({column_names}) VALUES ({placeholders})
                    ON CONFLICT (iccid) DO UPDATE SET {set_clause}
                """
            elif target_table == 'workers':
                columns = list(clean_row.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join(columns)
                set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'worker_id'])
                upsert_query = f"""
                    INSERT INTO workers ({column_names}) VALUES ({placeholders})
                    ON CONFLICT (worker_id) DO UPDATE SET {set_clause}
                """
            
            cursor.execute(upsert_query, list(clean_row.values()))
            row_count += 1
        
        db.commit()
        cursor.close()
        
        current_app.logger.info("CSV import completed successfully: %d rows processed for table '%s' by user %s", 
                       row_count, target_table, session.get('username'))
        return jsonify({"message": f"Successfully processed {row_count} rows."}), 200
        
    except Exception as e:
        if 'db' in locals():
            db.rollback()
        if 'cursor' in locals():
            cursor.close()
        current_app.logger.error("CSV import failed for table '%s' by user %s: %s", 
                        target_table, session.get('username'), e, exc_info=True)
        return jsonify({"error": "An error occurred during CSV processing.", "details": str(e)}), 500

@api_bp.route('/admin/all_workers_status', methods=['GET'])
@login_required
@role_required('Administrator')
def get_admin_all_workers_status():
    """
    API endpoint to get the status of ALL workers and their assigned assets.
    """
    db = get_db()
    cursor = db.cursor()
    
    # FIXED QUERY: Added ::text to rh.worker_id to cast it to text for the JOIN.
    # This resolves the "operator does not exist" error.
    query = """
        SELECT
            w.id AS worker_db_id,
            w.worker_id,
            w.full_name AS worker_name,
            w.status,
            COALESCE(rh.contract_type, 'CDI') AS contract_type,
            rh.contract_end_date,
            rh.id_philia,
            rh.mdp_philia,
            s.secteur_name,
            s.id AS secteur_id,
            p.id AS phone_id,
            p.asset_tag,
            p.manufacturer,
            p.model,
            p.status AS phone_status,
            pn.phone_number,
            sc.carrier,
            COALESCE(open_tickets.ticket_count, 0) AS open_ticket_count,
            COALESCE(swap_info.pending_swaps, 0) AS pending_swaps,
            swap_info.latest_swap_initiated,
            swap_info.swap_ticket_id,
            COALESCE(total_tickets.total_tickets, 0) AS total_tickets,
            COALESCE(phone_history.total_phones, 0) AS total_phones
        FROM workers w
        LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
        LEFT JOIN phones p ON a.phone_id = p.id
        LEFT JOIN sim_cards sc ON a.sim_card_id = sc.id
        LEFT JOIN phone_numbers pn ON sc.id = pn.sim_card_id
        LEFT JOIN secteurs s ON w.secteur_id = s.id
        LEFT JOIN rh_data rh ON w.worker_id = rh.worker_id::text
        LEFT JOIN (
            SELECT 
                t.phone_id,
                COUNT(*) AS ticket_count
            FROM tickets t
            WHERE t.status NOT IN ('Solved', 'Closed')
            GROUP BY t.phone_id
        ) open_tickets ON p.id = open_tickets.phone_id
        LEFT JOIN (
            SELECT 
                t.phone_id,
                COUNT(*) AS pending_swaps,
                MAX(tu.created_at) AS latest_swap_initiated,
                MAX(t.id) AS swap_ticket_id
            FROM tickets t
            JOIN ticket_updates tu ON t.id = tu.ticket_id
            WHERE tu.update_text LIKE %s
            AND t.status NOT IN ('Solved', 'Closed')
            GROUP BY t.phone_id
        ) swap_info ON p.id = swap_info.phone_id
        LEFT JOIN (
            SELECT 
                p2.id as phone_id,
                COUNT(DISTINCT t2.id) AS total_tickets
            FROM phones p2
            LEFT JOIN tickets t2 ON p2.id = t2.phone_id
            GROUP BY p2.id
        ) total_tickets ON p.id = total_tickets.phone_id
        LEFT JOIN (
            SELECT 
                a2.worker_id,
                COUNT(*) AS total_phones
            FROM assignments a2
            GROUP BY a2.worker_id
        ) phone_history ON w.id = phone_history.worker_id
        ORDER BY s.secteur_name, w.full_name;
    """
    
    cursor.execute(query, ('%PHONE SWAP INITIATED%',))
    all_workers_status = cursor.fetchall()
    cursor.close()
    
    return jsonify(all_workers_status)

@api_bp.route('/admin/worker/<int:worker_db_id>', methods=['PUT'])
@login_required
@role_required('Administrator')
def update_worker_details(worker_db_id):
    """
    Update complete worker information.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # --- Update workers table ---
        worker_fields = ['worker_id', 'full_name', 'status', 'secteur_id']
        worker_update_fields = []
        worker_values = []
        for field in worker_fields:
            if field in data:
                worker_update_fields.append(f"{field} = %s")
                worker_values.append(data[field])
        
        if worker_update_fields:
            worker_values.append(worker_db_id)
            cursor.execute(f"UPDATE workers SET {', '.join(worker_update_fields)} WHERE id = %s", worker_values)
        
        # --- Handle rh_data table update/insert ---
        rh_fields = ['contract_type', 'contract_end_date', 'id_philia', 'mdp_philia']
        rh_data = {k: v for k, v in data.items() if k in rh_fields}
        
        if rh_data:
            # FIXED: Convert empty string for date to None (SQL NULL)
            if 'contract_end_date' in rh_data and rh_data['contract_end_date'] == '':
                rh_data['contract_end_date'] = None

            # Filter out password field if it's empty
            if 'mdp_philia' in rh_data and not rh_data['mdp_philia']:
                del rh_data['mdp_philia']

            if rh_data: # Proceed only if there's data left to update
                cursor.execute("SELECT worker_id FROM workers WHERE id = %s", (worker_db_id,))
                worker_result = cursor.fetchone()

                if worker_result:
                    worker_id = worker_result['worker_id']
                    
                    rh_update_fields = [f"{field} = %s" for field in rh_data.keys()]
                    rh_values = list(rh_data.values())
                    rh_values.append(worker_id)
                    
                    cursor.execute(
                        f"UPDATE rh_data SET {', '.join(rh_update_fields)} WHERE worker_id::text = %s", 
                        rh_values
                    )
                    
                    if cursor.rowcount == 0:
                        # If no record was updated, insert a new one
                        columns = ['worker_id'] + list(rh_data.keys())
                        placeholders = ', '.join(['%s'] * len(columns))
                        insert_values = [worker_id] + list(rh_data.values())
                        cursor.execute(f"INSERT INTO rh_data ({', '.join(columns)}) VALUES ({placeholders})", insert_values)
        
        db.commit()
        
        # --- Fetch and return the fully updated worker data ---
        query = """
            SELECT
                w.id AS worker_db_id,
                w.worker_id,
                w.full_name AS worker_name,
                w.status,
                COALESCE(rh.contract_type, 'CDI') AS contract_type,
                rh.contract_end_date,
                rh.id_philia,
                rh.mdp_philia,
                s.secteur_name,
                s.id AS secteur_id
            FROM workers w
            LEFT JOIN secteurs s ON w.secteur_id = s.id
            LEFT JOIN rh_data rh ON w.worker_id = rh.worker_id::text
            WHERE w.id = %s;
        """
        cursor.execute(query, (worker_db_id,))
        updated_worker_data = cursor.fetchone()
        
        cursor.close()
        
        return jsonify(updated_worker_data), 200
        
    except Exception as e:
        db.rollback()
        cursor.close()
        current_app.logger.error("Error updating worker %s: %s", worker_db_id, e, exc_info=True)
        return jsonify({"error": str(e)}), 500