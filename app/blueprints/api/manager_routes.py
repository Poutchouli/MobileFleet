# app/blueprints/api/manager_routes.py
# Manager API routes.

from flask import request, jsonify, current_app, session
from . import api_bp
from app.utils.decorators import login_required, role_required
from app.utils.helpers import get_db

@api_bp.route('/manager/team_status', methods=['GET'])
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
    # It also gets details of their currently assigned phone, a count of any open tickets,
    # and information about pending phone swaps.
    query = """
        SELECT
            w.id AS worker_id,
            w.full_name AS worker_name,
            p.id AS phone_id,
            p.asset_tag,
            p.manufacturer,
            p.model,
            p.status AS phone_status,
            COALESCE(open_tickets.ticket_count, 0) AS open_ticket_count,
            COALESCE(swap_info.pending_swaps, 0) AS pending_swaps,
            swap_info.latest_swap_initiated,
            swap_info.swap_ticket_id
        FROM workers w
        LEFT JOIN assignments a ON w.id = a.worker_id AND a.return_date IS NULL
        LEFT JOIN phones p ON a.phone_id = p.id
        JOIN secteurs s ON w.secteur_id = s.id
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
        WHERE s.manager_id = %s
        ORDER BY w.full_name;
    """
    
    cursor.execute(query, ('%PHONE SWAP INITIATED%', manager_id))
    team_status = cursor.fetchall()
    cursor.close()
    
    return jsonify(team_status)

@api_bp.route('/manager/selectable_phones', methods=['GET'])
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

@api_bp.route('/manager/tickets', methods=['GET'])
@login_required
@role_required('Manager')
def get_manager_tickets():
    """API endpoint to get all tickets submitted by the current manager."""
    manager_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()
    
    query = """
        SELECT 
            t.id AS ticket_id,
            t.title,
            t.status,
            t.priority,
            t.created_at,
            t.updated_at,
            w.full_name AS worker_name,
            p.asset_tag,
            p.manufacturer,
            p.model
        FROM tickets t
        LEFT JOIN phones p ON t.phone_id = p.id
        LEFT JOIN assignments a ON p.id = a.phone_id AND a.return_date IS NULL
        LEFT JOIN workers w ON a.worker_id = w.id
        WHERE t.submitted_by = %s
        ORDER BY t.created_at DESC
    """
    
    cursor.execute(query, (manager_id,))
    tickets = cursor.fetchall()
    cursor.close()
    
    return jsonify(tickets)
