from flask import Blueprint, render_template, request, session
from app.utils.auth import login_required
from config.db import db
from app.models.transaction_model import Transaction, Card
from app.models.category_model import Category
from datetime import datetime
from flask import make_response
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

@dashboard_bp.route("/export-pdf")
@login_required
def export_pdf():
    user_id = session.get("user_id")
    selected_month = request.args.get("month", "all")

    query = Transaction.query.filter_by(user_id=user_id)

    month_label = "Tous les mois"

    if selected_month != "all":
        query = query.filter(
            db.extract("month", Transaction.created_at) == int(selected_month)
        )

        months = [
            "Janvier", "Février", "Mars", "Avril",
            "Mai", "Juin", "Juillet", "Août",
            "Septembre", "Octobre", "Novembre", "Décembre"
        ]

        month_label = months[int(selected_month) - 1]

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

    category_stats = {}

    for t in transactions:
        if t.type == "expense":
            if t.category not in category_stats:
                category_stats[t.category] = 0

            category_stats[t.category] += t.amount

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("<b>Pluma - Rapport financier Dashboard</b>", styles["Title"])
    )

    elements.append(
        Paragraph(f"Période : {month_label}", styles["Heading2"])
    )

    elements.append(Spacer(1, 18))

    kpi_data = [
        ["Indicateur", "Montant"],
        ["My Balance", f"{my_balance:.2f}"],
        ["Income", f"{income:.2f}"],
        ["Expense", f"{expense:.2f}"],
        ["Total Saving", f"{total_saving:.2f}"],
    ]

    kpi_table = Table(kpi_data, colWidths=[220, 220])

    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24006d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f4f6fa")
        ]),
        ("PADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(kpi_table)
    elements.append(Spacer(1, 22))

    elements.append(
        Paragraph("<b>Dépenses par catégorie</b>", styles["Heading2"])
    )

    category_data = [["Catégorie", "Montant", "Pourcentage"]]

    total_expense_categories = sum(category_stats.values())

    for category, amount in category_stats.items():
        percent = 0

        if total_expense_categories > 0:
            percent = (amount / total_expense_categories) * 100

        category_data.append([
            category,
            f"{amount:.2f}",
            f"{percent:.1f}%"
        ])

    if len(category_data) == 1:
        category_data.append(["Aucune dépense", "0.00", "0%"])

    category_table = Table(category_data, colWidths=[180, 130, 130])

    category_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24006d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f4f6fa")
        ]),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(category_table)
    elements.append(Spacer(1, 22))

    elements.append(
        Paragraph("<b>Historique des transactions</b>", styles["Heading2"])
    )

    transaction_data = [[
        "Date", "Description", "ID", "Catégorie", "Carte", "Montant"
    ]]

    for t in transactions:
        amount = f"+{t.amount:.2f}" if t.type == "income" else f"-{t.amount:.2f}"

        transaction_data.append([
            t.created_at.strftime("%d/%m/%Y %H:%M"),
            t.title,
            t.transaction_code,
            t.category,
            t.card or "Cash",
            amount
        ])

    if len(transaction_data) == 1:
        transaction_data.append([
            "-", "Aucune transaction", "-", "-", "-", "0.00"
        ])

    transaction_table = Table(
        transaction_data,
        colWidths=[80, 140, 70, 80, 70, 70],
        repeatRows=1
    )

    transaction_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24006d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f4f6fa")
        ]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(transaction_table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"inline; filename=dashboard_report_{selected_month}.pdf"
    )

    return response