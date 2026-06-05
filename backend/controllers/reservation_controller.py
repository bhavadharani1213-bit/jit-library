from flask import request, jsonify
from datetime import datetime, timedelta
from models import db
from models.book import Book
from models.reservation import Reservation
from models.notification import Notification
from models.user import User   # ✅ make sure User is imported


# ✅ Helper: Create a notification
def create_notification(user_id, message):
    note = Notification(
        user_id=user_id,
        message=message,
        timestamp=datetime.utcnow(),
        seen=False
    )
    db.session.add(note)


# ✅ Reserve a book
def reserve_book():
    data = request.get_json()
    book_id = data.get("book_id")
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if book.available_count <= 0:
        return jsonify({"error": "Book not available"}), 400

    reservation = Reservation(
        user_id=user.id,
        book_id=book_id,
        status="reserved",
        reserved_date=datetime.utcnow()
    )

    book.available_count -= 1
    db.session.add(reservation)

    create_notification(user.id, f"You reserved '{book.title}' successfully.")
    db.session.commit()

    return jsonify({"message": "Book reserved successfully"}), 201


# ✅ Borrow a book
def borrow_book():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    reservation.status = "borrowed"
    reservation.borrowed_at = datetime.utcnow()
    reservation.due_date = datetime.utcnow() + timedelta(days=14)

    create_notification(reservation.user_id, f"You borrowed '{reservation.book.title}'.")
    db.session.commit()

    return jsonify({"message": "Book borrowed successfully"}), 200


# ✅ Return a book
def return_book():
    data = request.get_json()
    reservation_id = data.get("reservation_id")

    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    reservation.status = "returned"
    reservation.returned_at = datetime.utcnow()

    # Fine calculation
    if reservation.due_date and reservation.returned_at > reservation.due_date:
        days_overdue = (reservation.returned_at - reservation.due_date).days
        reservation.fine_amount = days_overdue * 5
    else:
        reservation.fine_amount = 0

    # Restore book count
    book = Book.query.get(reservation.book_id)
    if book:
        book.available_count += 1

    create_notification(reservation.user_id, f"You returned '{book.title}' successfully.")
    db.session.commit()

    return jsonify({
        "message": "Book returned successfully",
        "fine": reservation.fine_amount
    }), 200


# ✅ Get user books (active)
def get_user_books():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    reservations = Reservation.query.filter_by(user_id=user.id).filter(
        Reservation.status.in_(["reserved", "borrowed"])
    ).all()

    book_ids = [r.book_id for r in reservations]
    books = {b.id: b for b in Book.query.filter(Book.id.in_(book_ids)).all()}

    return jsonify([{
        "id": r.id,
        "book_title": books[r.book_id].title if r.book_id in books else None,
        "status": r.status,
        "reserved_date": r.reserved_date
    } for r in reservations])


# ✅ Get borrowing history
def get_borrowing_history():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    reservations = Reservation.query.filter_by(user_id=user.id).all()

    book_ids = [r.book_id for r in reservations]
    books = {b.id: b for b in Book.query.filter(Book.id.in_(book_ids)).all()}

    return jsonify([{
        "id": r.id,
        "book_title": books[r.book_id].title if r.book_id in books else None,
        "status": r.status,
        "reserved_date": r.reserved_date,
        "borrowed_at": r.borrowed_at,
        "returned_at": r.returned_at,
        "due_date": r.due_date,
        "fine_amount": r.fine_amount
    } for r in reservations])


# ✅ Get due soon reminders
def get_due_soon_reminders():
    today = datetime.utcnow().date()
    soon_date = today + timedelta(days=3)

    reservations = Reservation.query.filter(
        Reservation.status == "borrowed",
        Reservation.due_date != None
    ).all()

    reminders = []

    for r in reservations:
        if r.due_date and r.due_date.date() <= soon_date:
            reminders.append({
                "id": r.id,
                "book_title": r.book.title,
                "due_date": r.due_date
            })

        # Mark overdue
        if r.due_date and r.due_date.date() < today:
            r.status = "overdue"

    db.session.commit()
    return jsonify(reminders)
