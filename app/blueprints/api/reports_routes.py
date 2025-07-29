# app/blueprints/api/reports_routes.py
# API routes for dashboard reporting.

from flask import jsonify, current_app
from . import api_bp
from app.utils.decorators import login_required
from app.utils.helpers import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@api_bp.route('/reports/summary_stats', methods=['GET'])
@login_required
def get_summary_stats():
    """API endpoint for dashboard summary statistics."""
    try:
        db = get_db()
        cursor = db.cursor()

        # Query for active workers
        cursor.execute("SELECT COUNT(*) AS count FROM workers WHERE status = 'Active'")
        active_workers = cursor.fetchone()['count']

        # Query for phones in use
        cursor.execute("SELECT COUNT(*) AS count FROM phones WHERE status = 'In Use'")
        phones_in_use = cursor.fetchone()['count']
        
        # Query for phones in stock
        cursor.execute("SELECT COUNT(*) AS count FROM phones WHERE status = 'In Stock'")
        phones_in_stock = cursor.fetchone()['count']

        # Query for open tickets
        cursor.execute("SELECT COUNT(*) AS count FROM tickets WHERE status NOT IN ('Solved', 'Closed')")
        open_tickets = cursor.fetchone()['count']

        cursor.close()

        stats = {
            'active_workers': active_workers,
            'phones_in_use': phones_in_use,
            'phones_in_stock': phones_in_stock,
            'open_tickets': open_tickets
        }
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Failed to fetch summary stats: {e}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve summary stats: {str(e)}"}), 500

@api_bp.route('/reports/dashboard_charts', methods=['GET'])
@login_required
def get_dashboard_charts():
    """API endpoint for dashboard chart data."""
    try:
        db = get_db()
        cursor = db.cursor()

        # Helper to format chart data correctly using dictionary keys
        def format_chart_data(data, label_key, value_key):
            labels = [row[label_key] for row in data]
            values = [float(row[value_key]) for row in data] # Ensure values are numbers
            # Define some color palettes
            colors = [
                '#36A2EB', '#FF6384', '#FFCE56', '#4BC0C0', 
                '#9966FF', '#FF9F40', '#4D5360', '#C9CBCF'
            ]
            return {"labels": labels, "data": values, "backgroundColors": colors[:len(labels)]}

        # --- Data for Phones by Status Chart ---
        cursor.execute("SELECT status, COUNT(*) as count FROM phones GROUP BY status")
        phones_by_status_data = cursor.fetchall()
        
        # --- Data for Tickets by Priority Chart ---
        cursor.execute("SELECT priority, COUNT(*) as count FROM tickets WHERE status NOT IN ('Solved', 'Closed') GROUP BY priority")
        tickets_by_priority_data = cursor.fetchall()
        
        # --- Data for SIM Cards by Carrier Chart ---
        cursor.execute("SELECT carrier, COUNT(*) as count FROM sim_cards GROUP BY carrier")
        sim_cards_by_carrier_data = cursor.fetchall()

        # --- Data for Workers by Sector Chart ---
        cursor.execute("""
            SELECT s.secteur_name, COUNT(w.id) as count 
            FROM workers w 
            JOIN secteurs s ON w.secteur_id = s.id 
            WHERE w.status = 'Active'
            GROUP BY s.secteur_name
        """)
        workers_by_sector_data = cursor.fetchall()

        # --- Data for Assignment Trends (Last 6 Months) ---
        cursor.execute("""
            SELECT TO_CHAR(assignment_date, 'YYYY-MM') as month, COUNT(*) as count
            FROM assignments
            WHERE assignment_date >= NOW() - INTERVAL '6 months'
            GROUP BY month
            ORDER BY month
        """)
        assignment_trends_data = cursor.fetchall()
        
        # --- Data for Ticket Resolution Time ---
        cursor.execute("""
            SELECT 
                priority, 
                COALESCE(AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/86400), 0) as avg_days
            FROM tickets
            WHERE status IN ('Solved', 'Closed')
            GROUP BY priority
        """)
        ticket_resolution_time_data = cursor.fetchall()
        
        cursor.close()

        # --- Construct final JSON response with correct function calls ---
        chart_data = {
            "phones_by_status": format_chart_data(phones_by_status_data, 'status', 'count'),
            "tickets_by_priority": format_chart_data(tickets_by_priority_data, 'priority', 'count'),
            "sim_cards_by_carrier": format_chart_data(sim_cards_by_carrier_data, 'carrier', 'count'),
            "workers_by_sector": format_chart_data(workers_by_sector_data, 'secteur_name', 'count'),
            "assignment_trends": format_chart_data(assignment_trends_data, 'month', 'count'),
            "ticket_resolution_time": format_chart_data(ticket_resolution_time_data, 'priority', 'avg_days')
        }
        
        # Add specific styles for the line chart
        line_chart_styles = {
            "borderColor": "#36A2EB",
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
        }
        chart_data["assignment_trends"].update(line_chart_styles)

        return jsonify(chart_data)

    except Exception as e:
        current_app.logger.error(f"Failed to fetch dashboard chart data: {e}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve chart data: {str(e)}"}), 500
