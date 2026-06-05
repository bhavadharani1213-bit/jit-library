from flask import jsonify
from models.user import User
from models.book import Book
from models.reservation import Reservation
from models.book_request import BookRequest
from flask import request
from models import db
from flask_login import login_required




def get_dashboard_stats():
    stats = {
        "total_users": User.query.count(),
        "total_books": Book.query.count(),
        "books_reserved": Reservation.query.filter_by(status="reserved").count(),
        "books_borrowed": Reservation.query.filter_by(status="borrowed").count(),
        "books_returned": Reservation.query.filter_by(status="returned").count(),
        "pending_book_requests": BookRequest.query.filter_by(status="pending").count()
    }

    return jsonify(stats), 200

# 📊 Get single user login stats

@login_required
def get_user_login_stats():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user_id": user.id,
        "name": user.name,
        "login_count": user.login_count,
        "last_login": user.last_login
    }), 200


# 📋 Get all users

@login_required
def get_all_users():
    users = User.query.all()
    result = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "department": u.department,
        "is_active": u.is_active,
        "login_count": u.login_count,
        "last_login": u.last_login
    } for u in users]
    return jsonify(result), 200


# 🛑 Deactivate user

@login_required
def deactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated"}), 200


# 🔓 Reactivate user

@login_required
def reactivate_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_active = True
    db.session.commit()
    return jsonify({"message": "User reactivated"}), 200


# 🏫 Get users by department

@login_required
def get_users_by_department():
    dept = request.args.get("department")
    if not dept:
        return jsonify({"error": "Department is required"}), 400

    users = User.query.filter_by(department=dept).all()
    result = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "is_active": u.is_active
    } for u in users]

    return jsonify(result), 200

