from flask import request, jsonify
from models.user import User
from models import db
from werkzeug.security import generate_password_hash, check_password_hash

# 👀 View Profile
def view_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "login_count": user.login_count,
        "last_login": user.last_login
    }), 200

# ✏️ Edit Profile Info (name, email, department)
def edit_profile(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.department = data.get("department", user.department)

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200

# 🔐 Change Password
def change_password(user_id):
    data = request.get_json()
    old_pw = data.get("old_password")
    new_pw = data.get("new_password")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not old_pw or not new_pw:
        return jsonify({"error": "Both old and new passwords are required"}), 400

    if not check_password_hash(user.password, old_pw):
        return jsonify({"error": "Old password is incorrect"}), 401

    user.password = generate_password_hash(new_pw)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
