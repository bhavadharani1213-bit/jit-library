from flask import Blueprint
from controllers.admin_controller import get_dashboard_stats
from controllers.admin_controller import get_user_login_stats
from controllers.admin_controller import (
    get_all_users,
    deactivate_user,
    reactivate_user,
    get_users_by_department
)
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from flask_login import login_required, current_user
from controllers.admin_controller import get_dashboard_stats, get_user_login_stats
from controllers.admin_controller import get_all_users, deactivate_user, reactivate_user, get_users_by_department
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from models.admin import Admin
from models import db
from models.user import User
from utils.decorators import admin_required
from controllers import admin_controller as ac

admin_bp = Blueprint('admin', __name__)
admin_bp.route('/dashboard-stats', methods=['GET'])(ac.get_dashboard_stats)
admin_bp.route('/users/login_stats', methods=['GET'])(ac.get_user_login_stats)
admin_bp.route('/users', methods=['GET'])(get_all_users)
admin_bp.route('/user/<int:user_id>/deactivate', methods=['PUT'])(deactivate_user)
admin_bp.route('/user/<int:user_id>/reactivate', methods=['PUT'])(reactivate_user)
admin_bp.route('/users/by-department', methods=['GET'])(get_users_by_department)


@admin_bp.route('/profile', methods=['GET'])
@login_required
def get_admin_profile():
    from app import get_db
    db = get_db()

    row = db.execute(
        "SELECT * FROM users WHERE id = ? AND role = 'Admin'",
        (current_user.id,)
    ).fetchone()

    admin = Admin.from_row(row)
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    return jsonify(admin.__dict__)


@admin_bp.route('/profile', methods=['PUT'])
@login_required
def update_admin_profile():
    from app import get_db
    db = get_db()

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    department = data.get('department')

    db.execute('UPDATE users SET name = ?, email = ?, department = ? WHERE id = ?',
               (name, email, department, current_user.id))
    db.commit()
    return jsonify({'message': 'Profile updated successfully'})

@admin_bp.route('/change-password', methods=['PUT'])
@login_required
def change_password():
    from app import get_db  # lazy import to avoid circular

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'error': 'Both old and new password are required'}), 400

    db = get_db()
    admin = db.execute('SELECT password FROM users WHERE id = ?', (current_user.id,)).fetchone()
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    if not check_password_hash(admin['password'], old_password):
        return jsonify({'error': 'Old password is incorrect'}), 400

    hashed_pw = generate_password_hash(new_password)
    db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_pw, current_user.id))
    db.commit()

    return jsonify({'message': 'Password updated successfully'})

@admin_bp.route('/overview', methods=['GET'])
@login_required
def admin_overview():
    from app import get_db
    db = get_db()

    total_books = db.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    active_users = db.execute('SELECT COUNT(*) FROM users WHERE is_active = 1').fetchone()[0]
    pending_requests = db.execute('SELECT COUNT(*) FROM book_request WHERE status = "Pending"').fetchone()[0]
    total_fines = db.execute('SELECT IFNULL(SUM(fine_amount), 0) FROM reservations').fetchone()[0]

    return jsonify({
        'total_books': total_books,
        'active_users': active_users,
        'pending_requests': pending_requests,
        'total_fines': total_fines
    })

@admin_bp.route('/analytics', methods=['GET'])
@login_required
def admin_analytics():
    from app import get_db
    db = get_db()

    # Monthly borrow counts (last 6 months)
    borrow_trends = db.execute("""
        SELECT strftime('%m', borrowed_at) AS month, COUNT(*) as count
        FROM reservations
        WHERE borrowed_at >= date('now', '-6 months')
        GROUP BY month
        ORDER BY month
    """).fetchall()

    # Department-wise borrowing
    dept_borrow = db.execute("""
        SELECT u.department, COUNT(*) as count
        FROM reservations r
        JOIN users u ON r.user_id = u.id
        GROUP BY u.department
    """).fetchall()

    # Most borrowed books
    top_books = db.execute("""
        SELECT b.title, COUNT(*) as count
        FROM reservations r
        JOIN books b ON r.book_id = b.id
        GROUP BY r.book_id
        ORDER BY count DESC
        LIMIT 5
    """).fetchall()

    # Overdue and fines
    overdue_users = db.execute("""
        SELECT COUNT(*) FROM reservations
        WHERE returned_at IS NULL AND due_date < date('now')
    """).fetchone()[0]

    total_fines = db.execute("SELECT IFNULL(SUM(fine_amount), 0) FROM reservations").fetchone()[0]

    return jsonify({
        'borrow_trends': [dict(row) for row in borrow_trends],
        'dept_borrow': [dict(row) for row in dept_borrow],
        'top_books': [dict(row) for row in top_books],
        'overdue_users': overdue_users,
        'total_fines': total_fines
    })

def table_exists(db, table_name):
    try:
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
        return result is not None
    except sqlite3.Error:
        return False
    
@admin_bp.route('/books', methods=['GET'])
@login_required
def get_all_books():
    from app import get_db
    db = get_db()
    books = db.execute("SELECT * FROM books").fetchall()
    return jsonify([dict(row) for row in books])

@admin_bp.route('/books', methods=['POST'])
@login_required
def add_book():
    from app import get_db
    data = request.get_json()
    db = get_db()
    db.execute("""
        INSERT INTO books (title, author, isbn, category, quantity, ebook, publication, department)
        VALUES (?, ?, ?, ?, ?)
    """, (data['title'], data['author'], data['isbn'], data['category'], data['quantity'], data['ebook'], data['publication'], data['department']))
    db.commit()
    return jsonify({'message': 'Book added successfully'})

@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
@login_required
def update_book(book_id):
    from app import get_db
    data = request.get_json()
    db = get_db()
    db.execute("""
        UPDATE books
        SET title = ?, author = ?, isbn = ?, category = ?, quantity = ?, ebook = ?, publication = ?, department = ?
        WHERE id = ?
    """, (data['title'], data['author'], data['isbn'], data['category'], data['quantity'], data['ebook'], data['publication'], data['department'], book_id))
    db.commit()
    return jsonify({'message': 'Book updated successfully'})

@admin_bp.route('/books/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    from app import get_db
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    return jsonify({'message': 'Book deleted successfully'})

@admin_bp.route('/book_request', methods=['GET'])
@login_required
def get_book_requests():
    from app import get_db
    db = get_db()
    requests_data = db.execute("""
        SELECT br.id, br.user_id, u.name AS user_name, b.title AS book_title, 
               br.status, br.book_id, br.timestamp
        FROM book_request br
        JOIN users u ON br.user_id = u.id
        JOIN books b ON br.book_id = b.id
    """).fetchall()
    return jsonify([dict(row) for row in requests_data])


@admin_bp.route('/book_request/<int:request_id>/approve', methods=['PUT'])
@login_required
def approve_book_request(request_id):
    from app import get_db
    db = get_db()
    db.execute("UPDATE book_request SET status = 'Approved' WHERE id = ?", (request_id,))
    db.commit()
    return jsonify({'message': 'Book request approved'})

@admin_bp.route('/book_request/<int:request_id>/reject', methods=['PUT'])
@login_required
def reject_book_request(request_id):
    from app import get_db
    db = get_db()
    db.execute("UPDATE book_request SET status = 'Rejected' WHERE id = ?", (request_id,))
    db.commit()
    return jsonify({'message': 'Book request rejected'})

@admin_bp.route('/visit_log', methods=['GET'])
@login_required
def get_all_visits():
    from app import get_db
    db = get_db()
    visits = db.execute("""
        SELECT v.id, u.name AS user_name, v.action, v.timestamp
        FROM visit_log v
        JOIN users u ON v.user_id = u.id
        ORDER BY v.timestamp DESC
    """).fetchall()
    return jsonify([dict(row) for row in visits])


@admin_bp.route('/visit_log/checkin', methods=['POST'])
@login_required
def visit_checkin():
    from app import get_db
    data = request.get_json()
    db = get_db()
    db.execute("""
        INSERT INTO visit_log (user_id, action, timestamp)
        VALUES (?, 'checkin', datetime('now'))
    """, (data['user_id'],))
    db.commit()
    return jsonify({'message': 'User checked in'})


@admin_bp.route('/visit_log/checkout', methods=['POST'])
@login_required
def visit_checkout():
    from app import get_db
    data = request.get_json()
    db = get_db()
    db.execute("""
        INSERT INTO visit_log (user_id, action, timestamp)
        VALUES (?, 'checkout', datetime('now'))
    """, (data['user_id'],))
    db.commit()
    return jsonify({'message': 'User checked out'})
