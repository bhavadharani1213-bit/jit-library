from flask import request, jsonify
from models.book_request import BookRequest
from models import db
from utils.notify import create_notification
from models.user import User

def submit_request():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    author = data.get("author")
    reason = data.get("reason")

    if not user_id or not title:
        return jsonify({"error": "user_id and title are required"}), 400

    req = BookRequest(
        user_id=user_id,
        title=title,
        author=author,
        reason=reason
    )
    db.session.add(req)
    db.session.commit()

    return jsonify({"message": "Book request submitted"}), 201

def update_request_status():
    data = request.get_json()
    request_id = data.get("request_id")
    admin_id = data.get("admin_id")
    new_status = data.get("status")  # "approved" or "rejected"

    if not request_id or not admin_id or new_status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid input"}), 400

    
    book_request = BookRequest.query.get(request_id)
    admin = User.query.get(admin_id)

    if not book_request or not admin or admin.role.lower() != "admin":
        return jsonify({"error": "Request or admin not found or unauthorized"}), 403

    book_request.status = new_status
    db.session.commit()

    msg = f"Your book request for '{book_request.title}' was {new_status}."
    create_notification(book_request.user_id, msg)

    return jsonify({"message": f"Request {new_status}"}), 200

def get_user_requests():
    user_id = request.args.get("user_id")
    status = request.args.get("status")  # optional filter

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    query = BookRequest.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(BookRequest.timestamp.desc()).all()

    result = [{
        "id": r.id,
        "title": r.title,
        "author": r.author,
        "reason": r.reason,
        "status": r.status,
        "timestamp": r.timestamp
    } for r in requests]

    return jsonify(result), 200

def get_all_requests():
    admin_id = request.args.get("admin_id")
    status = request.args.get("status")  # optional

    admin = User.query.get(admin_id)
    if not admin or admin.role.lower() != "admin":
        return jsonify({"error": "Unauthorized. Admins only."}), 403

    query = BookRequest.query
    if status:
        query = query.filter_by(status=status)

    requests = query.order_by(BookRequest.timestamp.desc()).all()

    result = [{
        "id": r.id,
        "user_id": r.user_id,
        "book_id": r.book_id,
        "title": r.title,
        "author": r.author,
        "reason": r.reason,
        "status": r.status,
        "timestamp": r.timestamp
    } for r in requests]

    return jsonify(result), 200
