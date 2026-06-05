import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db
from models.reservation import Reservation
from models.book import Book
from models.notification import Notification
from models.user import User
from models.book_request import BookRequest
from models.visit_log import VisitLog
from dotenv import load_dotenv
from routes.auth_routes import auth_bp
from routes.book_routes import book_bp
from routes.reservation_routes import reservation_bp
from routes.notification_routes import notification_bp
from routes.book_request_routes import book_request_bp
from routes.admin_routes import admin_bp
from routes.visit_log_routes import visit_log_bp
from routes.user_routes import user_bp
from flask_login import LoginManager
from datetime import datetime, timedelta
from routes.feedback_routes import feedback_bp
from routes.borrow_routes import borrow_bp
from routes.fine_routes import fine_bp
import sqlite3

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5500"}}, supports_credentials=True)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'library.db')
print("DB path:", DB_PATH)

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "mysecret")
app.config['SESSION_COOKIE_SECURE'] = False

# DB init
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(book_bp, url_prefix='/api/books')
app.register_blueprint(reservation_bp, url_prefix='/api/reservations')
app.register_blueprint(notification_bp, url_prefix='/api/notifications')
app.register_blueprint(book_request_bp, url_prefix='/api/book_request')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(visit_log_bp, url_prefix='/api/visit')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(feedback_bp)
app.register_blueprint(borrow_bp)
app.register_blueprint(fine_bp)

# Create DB tables
with app.app_context():
    db.create_all()
    print("✅ All tables created successfully.")

# ---------- DB Connection Helper ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- APPROVE REQUEST ----------
@app.route('/api/book_request/<int:req_id>/approve', methods=['POST'])
def approve_request(req_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM book_request WHERE id = ?", (req_id,))
    req = cur.fetchone()

    if not req:
        conn.close()
        return jsonify({"error": "Request not found"}), 404
    if req["status"].lower() != "pending":
        conn.close()
        return jsonify({"error": "Request already processed"}), 400

    cur.execute("UPDATE book_request SET status = 'Approved' WHERE id = ?", (req_id,))
    cur.execute("""
        UPDATE books 
        SET available_count = available_count - 1, 
            reservation_count = reservation_count + 1 
        WHERE id = ?
    """, (req["book_id"],))
    conn.commit()
    conn.close()
    return jsonify({"message": "Request approved successfully"})

# ---------- REJECT REQUEST ----------
@app.route('/api/book_request/<int:req_id>/reject', methods=['POST'])
def reject_request(req_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM book_request WHERE id = ?", (req_id,))
    req = cur.fetchone()

    if not req:
        conn.close()
        return jsonify({"error": "Request not found"}), 404
    if req["status"].lower() != "pending":
        conn.close()
        return jsonify({"error": "Request already processed"}), 400

    cur.execute("UPDATE book_request SET status = 'Rejected' WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Request rejected successfully"})

# ---------- ANALYTICS ----------
@app.route('/api/admin/analytics/borrow-trends', methods=['GET'])
def analytics_borrow_trends():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', reserved_date) AS month, COUNT(*) AS count
        FROM reservations
        WHERE status = 'Approved'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/admin/analytics/department-borrowing', methods=['GET'])
def analytics_dept_borrowing():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.department, COUNT(r.id) AS count
        FROM reservations r
        JOIN books b ON r.book_id = b.id
        WHERE r.status = 'Approved'
        GROUP BY b.department
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/admin/analytics/most-borrowed', methods=['GET'])
def analytics_most_borrowed():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.title, COUNT(r.id) AS count
        FROM reservations r
        JOIN books b ON r.book_id = b.id
        WHERE r.status = 'Approved'
        GROUP BY b.id
        ORDER BY count DESC
        LIMIT 10
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

# ---------- LOGIN MANAGER ----------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login_user'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "Unauthorized"}), 401


if __name__ == '__main__':
    app.run(debug=True)
