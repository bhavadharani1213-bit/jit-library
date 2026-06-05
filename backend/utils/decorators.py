from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required

def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        
        if current_user.role.lower() != "admin":
            return jsonify({"error": "Unauthorized. Admins only."}), 403
        
        return f(*args, **kwargs)
    return wrapper
