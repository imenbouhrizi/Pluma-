from config.db import db
from datetime import datetime

class Category(db.Model):

    __tablename__="categories"

    id=db.Column(
        db.Integer,
        primary_key=True
    )

    name=db.Column(
        db.String(100),
        nullable=False
    )

    icon=db.Column(
        db.String(50),
        nullable=False
    )

    color=db.Column(
        db.String(20),
        nullable=False
    )

    type=db.Column(
        db.String(30),
        nullable=False
    )

    user_id=db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at=db.Column(
        db.DateTime,
        default=datetime.utcnow
    )