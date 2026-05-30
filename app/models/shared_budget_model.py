from config.db import db
from datetime import datetime


class SharedBudget(db.Model):
    __tablename__ = "shared_budgets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    total_amount = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0)
    remaining_amount = db.Column(db.Float, default=0)

    currency = db.Column(db.String(10), default="EUR")

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship("User", foreign_keys=[creator_id])

    categories = db.relationship(
        "SharedBudgetCategory",
        backref="shared_budget",
        cascade="all, delete-orphan"
    )

    members = db.relationship(
        "SharedBudgetMember",
        backref="shared_budget",
        cascade="all, delete-orphan"
    )

    invitations = db.relationship(
        "SharedBudgetInvitation",
        backref="shared_budget",
        cascade="all, delete-orphan"
    )

    expenses = db.relationship(
        "SharedBudgetExpense",
        backref="shared_budget",
        cascade="all, delete-orphan"
    )

    def calculate_remaining(self):
        self.spent_amount = sum(exp.amount for exp in self.expenses)
        self.remaining_amount = self.total_amount - self.spent_amount

    def __repr__(self):
        return f"<SharedBudget {self.name}>"


class SharedBudgetCategory(db.Model):
    __tablename__ = "shared_budget_categories"

    id = db.Column(db.Integer, primary_key=True)

    shared_budget_id = db.Column(
        db.Integer,
        db.ForeignKey("shared_budgets.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    category_ref = db.relationship("Category")


class SharedBudgetMember(db.Model):
    __tablename__ = "shared_budget_members"

    id = db.Column(db.Integer, primary_key=True)

    shared_budget_id = db.Column(
        db.Integer,
        db.ForeignKey("shared_budgets.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    role = db.Column(db.String(20), default="user")
    status = db.Column(db.String(20), default="accepted")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])


class SharedBudgetInvitation(db.Model):
    __tablename__ = "shared_budget_invitations"

    id = db.Column(db.Integer, primary_key=True)

    shared_budget_id = db.Column(
        db.Integer,
        db.ForeignKey("shared_budgets.id"),
        nullable=False
    )

    invited_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    invited_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    status = db.Column(db.String(20), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invited_user = db.relationship("User", foreign_keys=[invited_user_id])
    invited_by = db.relationship("User", foreign_keys=[invited_by_id])


class SharedBudgetExpense(db.Model):
    __tablename__ = "shared_budget_expenses"

    id = db.Column(db.Integer, primary_key=True)

    shared_budget_id = db.Column(
        db.Integer,
        db.ForeignKey("shared_budgets.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    added_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category_ref = db.relationship("Category")
    added_by = db.relationship("User", foreign_keys=[added_by_id])