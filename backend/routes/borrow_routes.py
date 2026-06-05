from flask import Blueprint, request, jsonify
from models import db
from models.borrowed import BorrowedBook
from models.book import Book
from models.user import User

borrow_bp = Blueprint('borrow', __name__)

@borrow_bp.route('/api/borrow/history', methods=['GET'])
def get_borrow_history():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    borrows = (
        db.session.query(BorrowedBook, Book)
        .join(Book, BorrowedBook.book_id == Book.id)
        .filter(BorrowedBook.user_id == user.id)
        .order_by(BorrowedBook.borrowed_on.desc())
        .all()
    )

    history = []
    for borrow, book in borrows:
        history.append({
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "borrow_date": borrow.borrowed_on.strftime("%B %d, %Y - %I:%M %p"),
            "return_date": borrow.returned_on.strftime("%B %d, %Y") if borrow.returned_on else None,
            "status": "Returned" if borrow.returned else "Borrowed"
        })

    return jsonify({"history": history})
