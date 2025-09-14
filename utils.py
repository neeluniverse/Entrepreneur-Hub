from datetime import datetime
from flask import flash
from models import db, Message

def get_unread_message_count(user_id):
    return Message.query.filter_by(recipient_id=user_id, read=False).count()

@app.context_processor
def inject_unread_count():
    if current_user.is_authenticated:
        return dict(unread_count=get_unread_message_count(current_user.id))
    return dict(unread_count=0)
