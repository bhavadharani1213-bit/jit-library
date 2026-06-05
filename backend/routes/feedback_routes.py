from flask import Blueprint, request, jsonify
from models import db
from models.feedback import Feedback  # ✅ import your ORM model

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    required = ["name", "email", "type", "message"]

    if not all(data.get(field) for field in required):
        return jsonify({"error": "All fields are required"}), 400

    try:
        new_feedback = Feedback(
            name=data["name"],
            email=data["email"],
            type=data["type"],
            message=data["message"]
        )
        db.session.add(new_feedback)  # ✅ ORM insert
        db.session.commit()

        return jsonify({"message": "Feedback submitted successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

