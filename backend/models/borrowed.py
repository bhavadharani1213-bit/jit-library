from models import db
from datetime import datetime

class BorrowedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    borrowed_on = db.Column(db.DateTime, default=datetime.utcnow)
    returned = db.Column(db.Boolean, default=False)
    returned_on = db.Column(db.DateTime, nullable=True)
