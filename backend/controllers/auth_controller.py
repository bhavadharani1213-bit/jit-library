from flask import request, jsonify
from models.user import User, db
from werkzeug.security import generate_password_hash
from datetime import datetime
from flask_login import login_user as flask_login_user

from models import db
def register_user():
    data = request.get_json()
    required = ["name", "email", "password", "phone", "ugid", "rollno", "department", "role"]

    for field in required:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    # Optional: year (students only)
    year = data.get("year") if data.get("role", "").lower() == "student" else None

    # Check if user already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    
    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"]),
        phone=data["phone"],
        ug_id=data["ugid"],
        roll_no=data["rollno"],
        department=data["department"],
        year=year,
        role=data["role"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # ✅ Log the user in (creates session cookie)
        flask_login_user(user)

        # ✅ Update login count and timestamp
        user.login_count += 1
        user.last_login = datetime.utcnow()
        db.session.commit()

        # ✅ Decide redirect URL based on role
        if user.role.lower() == "admin":
            redirect_url = "admin.html"
        else:
            redirect_url = "dashboard.html"

        return jsonify({
            "message": "Login successful",
            "user": {
                "name": user.name,
                "role": user.role,
                "email": user.email,
                "ug_id": user.ug_id,
                "id": user.id
            },
            "redirect": redirect_url
        }), 200

    return jsonify({"message": "Invalid email or password"}), 401

