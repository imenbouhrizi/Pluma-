from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import login_required
from config.db import db
from app.models.budget_model import Budget
from app.models.transaction_model import Transaction, Card
from datetime import datetime, timedelta
from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from app.models.notification_model import Notification
from io import BytesIO
import random

transaction_bp = Blueprint("transactions", __name__)

def get_card_balance(user_id, card_rib):
    card = Card.query.filter_by(
        user_id=user_id,
        rib=card_rib
    ).first()

    if not card:
        return None

    transactions = Transaction.query.filter_by(
        user_id=user_id,
        card=card_rib
    ).all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")

    return card.initial_balance + income - expense

def create_notification(user_id, title, message, notif_type):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notif_type,
        is_read=False
    )

    db.session.add(notification)

def sync_budget_by_keys(user_id, category, budget_name):
    if not category or not budget_name:
        return

    budget = Budget.query.filter_by(
        owner_id=user_id,
        category=category,
        name=budget_name
    ).first()

    if not budget:
        return

    budget_transaction = Transaction.query.filter_by(
        user_id=user_id,
        type="expense",
        category=category,
        description=budget_name,
        card="Budget"
    ).first()

    if budget_transaction:
        budget.spent_amount = budget_transaction.amount
    else:
        total_expense = db.session.query(
            db.func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.category == category,
            Transaction.description == budget_name
        ).scalar() or 0

        budget.spent_amount = total_expense

    budget.remaining_amount = budget.total_amount - budget.spent_amount

    if budget.spent_amount > budget.total_amount:
        existing = Notification.query.filter_by(
        user_id=user_id,
        type="budget_exceeded",
        related_id=budget.id,
        is_read=False
    ).first()

    if not existing:
        create_notification(
            user_id,
            "Budget dépassé",
            f"Le budget '{budget.name}' a dépassé sa limite de {budget.total_amount:.2f} {budget.currency}.",
            "budget_exceeded"
        )
        db.session.flush()
        Notification.query.order_by(Notification.id.desc()).first().related_id = budget.id


@transaction_bp.route("/")
@login_required
def index():
    user_id = session.get("user_id")

    filter_type = request.args.get("type", "all")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    page = request.args.get("page", 1, type=int)

    query = Transaction.query.filter_by(user_id=user_id)

    if filter_type == "income":
        query = query.filter_by(type="income")
    elif filter_type == "expense":
        query = query.filter_by(type="expense")

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Transaction.created_at >= start)
        except ValueError:
            flash("Date début invalide.", "danger")

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Transaction.created_at < end)
        except ValueError:
            flash("Date fin invalide.", "danger")

    transactions = query.order_by(Transaction.created_at.desc()).paginate(
        page=page,
        per_page=4,
        error_out=False
    )

    cards = Card.query.filter_by(
        user_id=user_id
    ).order_by(Card.created_at.asc()).all()

    card_stats = []

    for card in cards:
        card_transactions = Transaction.query.filter_by(
            user_id=user_id,
            card=card.rib
        ).all()

        income = sum(t.amount for t in card_transactions if t.type == "income")
        expense = sum(t.amount for t in card_transactions if t.type == "expense")

        card_stats.append({
            "id": card.id,
            "card_type": card.card_type,
            "rib": card.rib,
            "initial_balance": card.initial_balance,
            "income": income,
            "expense": expense,
            "current_balance": card.initial_balance + income - expense
        })

    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    current_month = datetime.now().month

    months_order = []

    for i in range(5, -1, -1):
        month_index = (current_month - 1 - i) % 12
        months_order.append(month_names[month_index])

    monthly_expenses = {month: 0 for month in months_order}

    expense_transactions = Transaction.query.filter_by(
        user_id=user_id,
        type="expense"
    ).all()

    for transaction in expense_transactions:
        month = transaction.created_at.strftime("%b")

        if month in monthly_expenses:
            monthly_expenses[month] += transaction.amount

    max_expense = max(monthly_expenses.values()) if monthly_expenses else 1

    if max_expense == 0:
        max_expense = 1

    monthly_chart = []

    for month, amount in monthly_expenses.items():
        height = int((amount / max_expense) * 125)

        if amount == 0:
            height = 70
        elif height < 45:
            height = 45

        monthly_chart.append({
            "month": month,
            "amount": amount,
            "height": height,
            "active": amount == max_expense and amount > 0
        })

    return render_template(
        "transactions.html",
        transactions=transactions,
        filter_type=filter_type,
        start_date=start_date,
        end_date=end_date,
        card_stats=card_stats,
        monthly_chart=monthly_chart
    )


@transaction_bp.route("/add-card", methods=["POST"])
@login_required
def add_card():
    user_id = session.get("user_id")

    card_type = request.form.get("card_type", "").strip()
    rib = request.form.get("rib", "").strip()

    try:
        initial_balance = float(request.form.get("initial_balance", 0))
    except ValueError:
        flash("Balance invalide.", "danger")
        return redirect(url_for("transactions.index"))

    if not card_type or not rib:
        flash("Veuillez remplir les informations de la carte.", "danger")
        return redirect(url_for("transactions.index"))

    existing_card = Card.query.filter_by(
        user_id=user_id,
        rib=rib
    ).first()

    if existing_card:
        flash("Cette carte existe déjà.", "warning")
        return redirect(url_for("transactions.index"))

    card = Card(
        card_type=card_type,
        rib=rib,
        initial_balance=initial_balance,
        user_id=user_id
    )

    db.session.add(card)
    db.session.commit()

    flash("Carte ajoutée avec succès.", "success")
    return redirect(url_for("transactions.index"))


@transaction_bp.route("/delete-card/<int:card_id>", methods=["POST"])
@login_required
def delete_card(card_id):
    user_id = session.get("user_id")

    card = Card.query.filter_by(
        id=card_id,
        user_id=user_id
    ).first()

    if not card:
        flash("Carte introuvable.", "danger")
        return redirect(url_for("transactions.index"))

    db.session.delete(card)
    db.session.commit()

    flash("Carte supprimée.", "info")
    return redirect(url_for("transactions.index"))


@transaction_bp.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session.get("user_id")

    title = request.form.get("title", "").strip()
    type_ = request.form.get("type")
    category = request.form.get("category", "").strip()
    card = request.form.get("card", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        flash("Montant invalide.", "danger")
        return redirect(url_for("transactions.index"))

    if not title or not type_ or not category or amount <= 0:
        flash("Veuillez remplir correctement les champs.", "danger")
        return redirect(url_for("transactions.index"))

    transaction_code = "#" + str(random.randint(10000000, 99999999))

    if type_ == "expense" and card and card != "Budget":
        balance = get_card_balance(user_id, card)

    if balance is not None and amount > balance:
        create_notification(
            user_id,
            "Transaction échouée",
            f"Solde insuffisant sur la carte {card}.",
            "transaction_failed"
        )

        db.session.commit()

        flash("Transaction refusée : solde insuffisant.", "danger")
        return redirect(url_for("transactions.index"))

    new_transaction = Transaction(
        title=title,
        transaction_code=transaction_code,
        amount=amount,
        type=type_,
        category=category,
        card=card,
        description=description,
        user_id=user_id
    )

    db.session.add(new_transaction)
    db.session.flush()

    if type_ == "expense":
        sync_budget_by_keys(user_id, category, description)

    db.session.commit()

    flash("Transaction ajoutée avec succès.", "success")
    return redirect(url_for("transactions.index"))


@transaction_bp.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete(transaction_id):
    user_id = session.get("user_id")

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=user_id
    ).first()

    if not transaction:
        flash("Transaction introuvable.", "danger")
        return redirect(url_for("transactions.index"))

    old_category = transaction.category
    old_description = transaction.description
    old_type = transaction.type

    db.session.delete(transaction)
    db.session.flush()

    if old_type == "expense":
        sync_budget_by_keys(user_id, old_category, old_description)

    db.session.commit()

    flash("Transaction supprimée.", "info")
    return redirect(url_for("transactions.index"))


@transaction_bp.route("/edit/<int:transaction_id>", methods=["POST"])
@login_required
def edit(transaction_id):
    user_id = session.get("user_id")

    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=user_id
    ).first()

    if not transaction:
        flash("Transaction introuvable.", "danger")
        return redirect(url_for("transactions.index"))

    old_category = transaction.category
    old_description = transaction.description
    old_type = transaction.type

    title = request.form.get("title", "").strip()
    type_ = request.form.get("type")
    category = request.form.get("category", "").strip()
    card = request.form.get("card", "").strip()
    description = request.form.get("description", "").strip()

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        flash("Montant invalide.", "danger")
        return redirect(url_for("transactions.index"))

    if not title or not type_ or not category or amount <= 0:
        flash("Veuillez remplir correctement les champs.", "danger")
        return redirect(url_for("transactions.index"))

    transaction.title = title
    transaction.amount = amount
    transaction.type = type_
    transaction.category = category
    transaction.card = card
    transaction.description = description

    db.session.flush()

    if old_type == "expense":
        sync_budget_by_keys(user_id, old_category, old_description)

    if type_ == "expense":
        sync_budget_by_keys(user_id, category, description)

    db.session.commit()

    flash("Transaction modifiée avec succès.", "success")
    return redirect(url_for("transactions.index"))


@transaction_bp.route("/export-pdf")
@login_required
def export_pdf():
    user_id = session.get("user_id")

    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        db.extract("month", Transaction.created_at) == 5
    ).order_by(Transaction.created_at.desc()).all()

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

    title = Paragraph("<b>Pluma - Historique des transactions</b>", styles["Title"])
    subtitle = Paragraph("Mois de Mai", styles["Heading2"])

    elements.append(title)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    data = [["Date", "Description", "ID", "Type", "Card", "Amount"]]

    for t in transactions:
        amount = f"+{t.amount:.2f}" if t.type == "income" else f"-{t.amount:.2f}"

        data.append([
            t.created_at.strftime("%d/%m/%Y"),
            t.title,
            t.transaction_code,
            t.category,
            t.card or "Cash",
            amount
        ])

    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24006d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f4f6fa")
        ]),
    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=transactions_mai.pdf"

    return response