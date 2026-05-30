from config.db import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False)

    message = db.Column(db.Text, nullable=False)

    type = db.Column(db.String(50), default="shared_budget")

    is_read = db.Column(db.Boolean, default=False)

    related_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Notification {self.title}>"