from config.db import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    transaction_code = db.Column(db.String(50), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # income / expense
    category = db.Column(db.String(50), nullable=False)

    card = db.Column(db.String(50), nullable=True)
    receipt = db.Column(db.String(255), nullable=True)

    description = db.Column(db.Text, nullable=True)
    #transaction normale, transaction créée depuis Budget

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.title}>"


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)

    card_type = db.Column(db.String(50), nullable=False)  # Visa / Mastercard / Cash
    rib = db.Column(db.String(50), nullable=False)
    initial_balance = db.Column(db.Float, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Card {self.card_type} - {self.rib}>"
    