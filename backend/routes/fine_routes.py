from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models.fine import Fine
from models import db

fine_bp = Blueprint("fines", __name__)

@fine_bp.route('/api/fines', methods=['GET'])
@login_required
def get_fines():
    fines = Fine.query.filter_by(user_id=current_user.id).all()
    result = []
    for fine in fines:
        result.append({
            "id": fine.id,
            "book_title": fine.book.title if fine.book else None,
            "amount": fine.amount,
            "reason": fine.reason,
            "created_on": fine.created_on.strftime("%Y-%m-%d"),
            "paid": fine.paid
        })
    return jsonify(result)

@fine_bp.route('/api/fines/pay/<int:fine_id>', methods=['POST'])
@login_required
def pay_fine(fine_id):
    fine = Fine.query.get(fine_id)
    if not fine or fine.user_id != current_user.id:
        return jsonify({"error": "Fine not found"}), 404

    fine.paid = True
    db.session.commit()
    return jsonify({"message": "Fine paid successfully"})

