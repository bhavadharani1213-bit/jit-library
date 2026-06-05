from flask import Blueprint, request, jsonify
from models.user import User
from models import db
from models.reservation import Reservation  
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.user_controller import view_profile, edit_profile, change_password

user_bp = Blueprint('user_routes', __name__)

# 👉 Profile-related endpoints
user_bp.route('/profile/<int:user_id>', methods=['GET'])(view_profile)
user_bp.route('/profile/<int:user_id>', methods=['PUT'])(edit_profile)
user_bp.route('/password/<int:user_id>', methods=['PUT'])(change_password)

# ✅ Borrowed and Reserved books - FIXED PATH
@user_bp.route('/borrowed-books', methods=['GET'])
def get_borrowed_books():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    books = []

    # 🟢 Borrowed books
    if hasattr(user, 'borrowed_books'):
        for b in user.borrowed_books:
            books.append({
                "title": b.book.title if b.book else "Unknown",
                "status": "Borrowed",
                "date": b.borrow_date.strftime("%B %d, %Y") if b.borrow_date else "N/A",
                "status_date_type": "Borrowed"
            })

    # 🟢 Reserved books
    if hasattr(user, 'reserved_books'):
        for r in user.reserved_books:
            books.append({
                "title": r.book.title if r.book else "Unknown",
                "status": "Reserved",
                "date": r.reserved_date.strftime("%B %d, %Y") if r.reserved_date else "N/A",
                "status_date_type": "Reserved"
            })

    return jsonify({"books": books}), 200
@user_bp.route('/all', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "email": u.email} for u in users])

