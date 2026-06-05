# visit_log_routes.py
from flask import Blueprint, request, jsonify
from models import db
from models.visit_log import VisitLog
from models.user import User

visit_log_bp = Blueprint('visit_log', __name__)

@visit_log_bp.route('/history', methods=['GET'])
def get_visit_history():
    email = request.args.get("email")  # safer than passing user_id directly

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Find the user_id from the email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch visit logs for this user
    logs = VisitLog.query.filter_by(user_id=user.id).order_by(VisitLog.entry_time.desc()).all()

    history = []
    for log in logs:
        history.append({
            "date": log.entry_time.strftime("%Y-%m-%d") if log.entry_time else "N/A",
            "time_in": log.entry_time.strftime("%I:%M %p") if log.entry_time else "N/A",
            "time_out": log.exit_time.strftime("%I:%M %p") if log.exit_time else "N/A"
        })

    return jsonify({"visits": history})
