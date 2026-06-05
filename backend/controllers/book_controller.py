from flask import request, jsonify
from models.book import Book
from models import db

# ✅ Add Book
def add_book():
    data = request.get_json()
    required_fields = ['title', 'author', 'isbn', 'department', 'category', 'available_count']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({"error": "Book with this ISBN already exists"}), 409

    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        publication=data.get('publication'),
        department=data['department'],
        category=data['category'],
        ebook_url=data.get('ebook_url'),
        available_count=int(data['available_count'])
    )
    db.session.add(book)
    db.session.commit()

    return jsonify({"message": "Book added successfully"}), 201


# 🗑️ Delete Book
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200


# ✏️ Edit Book
def edit_book(book_id):
    data = request.get_json()
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Update only if present in request
    for field in ['title', 'author', 'isbn', 'publication', 'department', 'category', 'ebook_url', 'available_count']:
        if field in data:
            setattr(book, field, data[field])

    db.session.commit()
    return jsonify({"message": "Book updated successfully"}), 200


# 📚 Get All Books
def get_all_books():
    books = Book.query.all()
    result = []
    for book in books:
        result.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication": book.publication,
            "department": book.department,
            "category": book.category,
            "ebook_url": book.ebook_url,
            "available_count": book.available_count
        })
    return jsonify(result), 200


# 📄 Get Book by ID
def get_book_by_id(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "publication": book.publication,
        "department": book.department,
        "category": book.category,
        "ebook_url": book.ebook_url,
        "available_count": book.available_count
    }), 200


def basic_book_search():
    query = request.args.get("q", "").strip().lower()

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    results = Book.query.filter(
        db.or_(
            Book.title.ilike(f"%{query}%"),
            Book.author.ilike(f"%{query}%")
        )
    ).all()

    return jsonify([{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "isbn": b.isbn,
        "department": b.department,
        "category": b.category,
        "available_count": b.available_count,
        "ebook_url": b.ebook_url
    } for b in results]), 200


# 🔬 2. Advanced Search (multiple filters)
def advanced_search():
    title = request.args.get("title")
    author = request.args.get("author")
    category = request.args.get("category")
    department = request.args.get("department")
    isbn = request.args.get("isbn")
    publication = request.args.get("publication")

    query = Book.query
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))
    if department:
        query = query.filter(Book.department.ilike(f"%{department}%"))
    if isbn:
        query = query.filter(Book.isbn.ilike(f"%{isbn}%"))
    if publication:
        query = query.filter(Book.publication.ilike(f"%{publication}%"))

    books = query.all()

    return jsonify([{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "isbn": b.isbn,
        "department": b.department,
        "category": b.category,
        "publication": b.publication,
        "available_count": b.available_count,
        "ebook_url": b.ebook_url
    } for b in books]), 200


# 📄 3. Get E-book URL
def get_ebook_url(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if not book.ebook_url:
        return jsonify({"message": "No e-book available for this book"}), 200

    return jsonify({
        "ebook_url": book.ebook_url
    }), 200