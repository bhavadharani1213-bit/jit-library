from flask import request, jsonify
from models import db
from models.user import User
from models.visit_log import VisitLog

# Mark a user's entry or exit
def mark_visit():
    data = request.get_json()
    user_id = data.get("user_id")
    action = data.get("action")  # Expected: "entry" or "exit"

    # Validate input
    if not user_id or action not in ["entry", "exit"]:
        return jsonify({"error": "user_id and valid action ('entry' or 'exit') are required"}), 400

    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create visit log
    log = VisitLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": f"{action.capitalize()} logged successfully"}), 200


# Get all visit logs for a specific user
def get_user_visit_logs():
    user_id = request.args.get("user_id")

    # Require user_id in query params
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    logs = VisitLog.query.filter_by(user_id=user_id) \
        .order_by(VisitLog.timestamp.desc()) \
        .all()

    result = [
        {
            "id": log.id,
            "action": log.action,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

    return jsonify(result), 200
