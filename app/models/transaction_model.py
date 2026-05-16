from config.db import db
from datetime import datetime

class Transaction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    amount = db.Column(db.Float)

    type = db.Column(db.String(20))

    category = db.Column(db.String(50))

    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))