from config.db import db
from datetime import datetime


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    type = db.Column(db.String(30), nullable=False)

    monthly_budget = db.Column(db.Float, default=0)

    total_amount = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0)
    remaining_amount = db.Column(db.Float, default=0)

    currency = db.Column(db.String(10), default="EUR")

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    period = db.Column(db.String(30), default="Monthly")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    is_shared = db.Column(db.Boolean, default=False)
    share_code = db.Column(db.String(50), nullable=True)

    category_ref = db.relationship("Category", backref="budgets")

    def calculate_remaining(self):
        self.remaining_amount = self.total_amount - self.spent_amount

    def __repr__(self):
        return f"<Budget {self.name}>"