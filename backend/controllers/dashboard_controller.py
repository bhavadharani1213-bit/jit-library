from flask import request, jsonify
from models.reservation import Reservation
from models.borrowed import BorrowedBook
from models.fine import Fine
from models.notification import Notification
from models.book import Book
from models.user import User
from models.user import db

def get_user_dashboard():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    # Reserved Books
    reserved = Reservation.query.filter_by(user_id=user_id).all()
    reserved_books = [{
        "title": r.book.title,
        "author": r.book.author,
        "reserved_on": r.timestamp
    } for r in reserved]

    # Borrowed Books
    borrowed = BorrowedBook.query.filter_by(user_id=user_id).all()
    borrowed_books = []
    returned_books = []

    for b in borrowed:
        book_info = {
            "title": b.book.title,
            "borrowed_on": b.borrowed_on,
            "returned": b.returned,
            "returned_on": b.returned_on
        }
        if b.returned:
            returned_books.append(book_info)
        else:
            borrowed_books.append(book_info)

    # Fines
    total_fine = db.session.query(db.func.sum(Fine.amount)).filter_by(user_id=user_id, paid=False).scalar() or 0.0

    # Notifications
    notes = Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).limit(5).all()
    notifications = [{
        "content": n.content,
        "seen": n.seen,
        "timestamp": n.timestamp
    } for n in notes]

    return jsonify({
        "reserved_books": reserved_books,
        "borrowed_books": borrowed_books,
        "returned_books": returned_books,
        "fines": total_fine,
        "notifications": notifications
    }), 200
