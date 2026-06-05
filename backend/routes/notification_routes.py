from flask import Blueprint
from controllers.notification_controller import get_notifications
from controllers.notification_controller import mark_as_seen

notification_bp = Blueprint('notifications', __name__)
notification_bp.route('/all', methods=['GET'])(get_notifications)
notification_bp.route('/seen', methods=['PUT'])(mark_as_seen)
