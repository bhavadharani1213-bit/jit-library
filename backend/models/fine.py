from models import db
from datetime import datetime

class Fine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))  # NEW
    amount = db.Column(db.Float)
    reason = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    paid = db.Column(db.Boolean, default=False)

    book = db.relationship('Book', backref='fines', lazy=True)

