from flask import Blueprint, request
from flask import request, jsonify
from models.book import Book

from controllers.book_controller import (
    add_book,
    delete_book,
    edit_book,
    get_all_books,
    get_book_by_id,
    basic_book_search,
    advanced_search,
    get_ebook_url
)
from utils.decorators import admin_required

book_bp = Blueprint('book', __name__)

# ✅ Add Book (Admin Only)
book_bp.route('/add', methods=['POST'])(admin_required(add_book))

# 🗑️ Delete Book by ID (Admin Only)
@book_bp.route('/delete/<int:book_id>', methods=['DELETE'])
@admin_required
def secured_delete(book_id):
    return delete_book(book_id)

# ✏️ Edit Book by ID (Admin Only)
@book_bp.route('/edit/<int:book_id>', methods=['PUT'])
@admin_required
def secured_edit(book_id):
    return edit_book(book_id)

# 📚 Get All Books (Public)
@book_bp.route('/all', methods=['GET'])
def fetch_all_books():
    return get_all_books()

# 📄 Get One Book by ID (Public)
@book_bp.route('/<int:book_id>', methods=['GET'])
def get_one_book(book_id):
    return get_book_by_id(book_id)

book_bp.route('/search', methods=['GET'])(basic_book_search)
book_bp.route('/advanced-search', methods=['GET'])(advanced_search)
book_bp.route('/ebook/<int:book_id>', methods=['GET'])(get_ebook_url)

@book_bp.route('/popular', methods=['GET'])
def most_reserved_books():
    books = Book.query.order_by(Book.reservation_count.desc()).limit(3).all()

    return jsonify({
        "books": [
            {"title": book.title, "author": book.author}
            for book in books
        ]
    })

@book_bp.route('/available', methods=['GET'])
def get_available_books():
    books = Book.query.filter(Book.available_count > 0).all()
    result = []
    for b in books:
        result.append({
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "category": b.category,
            "department": b.department,
            "available_count": b.available_count,
            "publication": b.publication,
            "year_of_publication": b.year_of_publication,
            "isbn": b.isbn,
            "created_at": b.created_at.strftime("%Y-%m-%d %H:%M:%S") if b.created_at else None,

            "is_ebook": b.is_ebook(),
            "ebook_url": b.ebook_url,
            "ebook_pdf_link": b.ebook_pdf_link,
            "reservation_count": b.reservation_count
        })
    return jsonify({"books": result})
