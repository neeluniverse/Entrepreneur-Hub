from models import Message
from flask import current_app
from flask_login import current_user

def get_unread_message_count(user_id):
    return Message.query.filter_by(recipient_id=user_id, read=False).count()
