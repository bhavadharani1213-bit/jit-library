from flask import request, jsonify
from models.notification import Notification
from models import db

def get_notifications():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    notes = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).all()
    result = [{
        "id": note.id,
        "message": note.message,
        "category": note.category,
        "timestamp": note.timestamp,
        "seen": note.seen
    } for note in notes]

    return jsonify(result), 200


def mark_as_seen():
    data = request.get_json()
    notification_id = data.get("notification_id")

    if not notification_id:
        return jsonify({"error": "notification_id is required"}), 400

    note = Notification.query.get(notification_id)
    if not note:
        return jsonify({"error": "Notification not found"}), 404

    note.seen = True
    db.session.commit()

    return jsonify({"message": "Notification marked as seen"}), 200
