# app/blueprints/api/general_routes.py
# General API routes that don't fit in specific categories.

from flask import jsonify, current_app
from . import api_bp
from app.utils.decorators import login_required, role_required
from app.utils.helpers import get_db

@api_bp.route('/sectors', methods=['GET'])
@login_required  
@role_required('Administrator')
def get_all_sectors():
    """
    Retourne une liste de tous les secteurs pour peupler les listes déroulantes.
    """
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id, secteur_name as name FROM secteurs ORDER BY secteur_name;")
    sectors = cursor.fetchall()
    cursor.close()
    
    return jsonify(sectors)
