from flask import Blueprint, render_template, request, session
from app.utils.auth import login_required
from config.db import db
from app.models.transaction_model import Transaction, Card
from app.models.category_model import Category
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    selected_month = request.args.get("month", "all")

    query = Transaction.query.filter_by(user_id=user_id)

    if selected_month != "all":
        query = query.filter(
            db.extract("month", Transaction.created_at) == int(selected_month)
        )

    transactions = query.order_by(Transaction.created_at.desc()).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")
    total_saving = income - expense

    cards = Card.query.filter_by(user_id=user_id).all()

    my_balance = 0

    for card in cards:
        card_transactions = Transaction.query.filter_by(
            user_id=user_id,
            card=card.rib
        ).all()

        card_income = sum(t.amount for t in card_transactions if t.type == "income")
        card_expense = sum(t.amount for t in card_transactions if t.type == "expense")

        my_balance += card.initial_balance + card_income - card_expense

    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    monthly_income = {month: 0 for month in month_names}
    monthly_expense = {month: 0 for month in month_names}

    chart_query = Transaction.query.filter_by(user_id=user_id)

    if selected_month != "all":
        chart_query = chart_query.filter(
            db.extract("month", Transaction.created_at) == int(selected_month)
        )

    chart_transactions = chart_query.all()

    for transaction in chart_transactions:
        month = transaction.created_at.strftime("%b")

        if transaction.type == "income":
            monthly_income[month] += transaction.amount
        elif transaction.type == "expense":
            monthly_expense[month] += transaction.amount

    category_stats = {}

    for transaction in transactions:
        if transaction.type == "expense":

            if transaction.category not in category_stats:

                category = Category.query.filter_by(
                    user_id=user_id,
                    name=transaction.category
                ).first()

                category_stats[transaction.category] = {
                    "amount": 0,
                    "color": category.color if category else "#7c4dff"
                }

            category_stats[transaction.category]["amount"] += transaction.amount

    total_category_expense = sum(
        data["amount"] for data in category_stats.values()
    )

    pie_data = []

    for name, data in category_stats.items():

        percent = 0

        if total_category_expense > 0:
            percent = round(
                (data["amount"] / total_category_expense) * 100,
                1
            )

        pie_data.append({
            "name": name,
            "amount": data["amount"],
            "percent": percent,
            "color": data["color"]
        })

    return render_template(
        "dashboard.html",
        selected_month=selected_month,
        my_balance=my_balance,
        income=income,
        expense=expense,
        total_saving=total_saving,
        transactions=transactions,
        pie_data=pie_data,
        monthly_income=list(monthly_income.values()),
        monthly_expense=list(monthly_expense.values()),
        month_labels=month_names
    )