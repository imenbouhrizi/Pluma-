from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.auth import login_required
from config.db import db
from app.models.budget_model import Budget
from app.models.category_model import Category
from datetime import datetime, timedelta

budget_bp = Blueprint("budgets", __name__)


def parse_date(date_value):
    if not date_value:
        return None
    return datetime.strptime(date_value, "%Y-%m-%d").date()


def get_current_monthly_budget(user_id):
    monthly_ref = Budget.query.filter_by(
        owner_id=user_id,
        is_shared=False
    ).filter(
        Budget.monthly_budget > 0
    ).order_by(
        Budget.created_at.desc()
    ).first()

    if monthly_ref:
        return monthly_ref.monthly_budget, monthly_ref.currency

    return 0, "EUR"


@budget_bp.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    selected_month = request.args.get("month", "all")

    selected_range = request.args.get("range", "6M")
    today = datetime.utcnow().date()
    
    if selected_range == "7D":
        start_filter = today.replace() - timedelta(days=7)
    elif selected_range == "30D":
        start_filter = today.replace() - timedelta(days=30)
    elif selected_range == "3M":
        start_filter = today.replace() - timedelta(days=90)
    elif selected_range == "6M":
        start_filter = today.replace() - timedelta(days=180)
    elif selected_range == "1Y":
        start_filter = today.replace() - timedelta(days=365)
        
    else:
        
        start_filter = None

    query = Budget.query.filter_by(
        owner_id=user_id,
        is_shared=False
    )
        
    if start_filter:
        query = query.filter(Budget.start_date >= start_filter)

    if selected_month != "all":
        query = query.filter(
            db.extract("month", Budget.created_at) == int(selected_month)
        )

    budgets = query.order_by(Budget.created_at.desc()).all()

    categories = Category.query.filter_by(
        user_id=user_id
    ).order_by(Category.name.asc()).all()

    total_budget, currency = get_current_monthly_budget(user_id)

    total_spent = sum(b.spent_amount or 0 for b in budgets)
    total_remaining = total_budget - total_spent

    category_totals = {}

    for b in budgets:
        cat_name = b.category or "Sans catégorie"

        if cat_name not in category_totals:
            category_totals[cat_name] = {
                "spent": 0,
                "color": b.category_ref.color if b.category_ref else "#7c4dff"
            }

        category_totals[cat_name]["spent"] += b.spent_amount or 0

    donut_parts = []
    start = 0

    if total_budget > 0:
        for data in category_totals.values():
            percent = (data["spent"] / total_budget) * 100
            end = start + percent

            if end > 100:
                end = 100

            if percent > 0:
                donut_parts.append(f'{data["color"]} {start}% {end}%')

            start = end

            if start >= 100:
                break

    if start < 100:
        donut_parts.append(f"#e8eaf1 {start}% 100%")

    donut_gradient = ", ".join(donut_parts) if donut_parts else "#e8eaf1 0% 100%"

    return render_template(
        "budgets.html",
        budgets=budgets,
        categories=categories,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_remaining,
        category_totals=category_totals,
        donut_gradient=donut_gradient,
        selected_month=selected_month,
        selected_range=selected_range,
        currency=currency
    )


@budget_bp.route("/add-category", methods=["POST"])
@login_required
def add_category():
    user_id = session.get("user_id")

    name = request.form.get("name", "").strip()
    icon = request.form.get("icon", "").strip()
    color = request.form.get("color", "#7c4dff").strip()

    if not name or not icon:
        flash("Veuillez remplir tous les champs de la catégorie.", "danger")
        return redirect(url_for("budgets.index"))

    new_category = Category(
        name=name,
        icon=icon,
        color=color,
        type="expense",
        user_id=user_id
    )

    db.session.add(new_category)
    db.session.commit()

    flash("Catégorie ajoutée avec succès.", "success")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/delete-category/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    user_id = session.get("user_id")

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        flash("Catégorie introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    related_budgets = Budget.query.filter_by(
        category_id=category.id,
        owner_id=user_id
    ).all()

    for budget in related_budgets:
        budget.category_id = None
        budget.category = "Sans catégorie"

    db.session.delete(category)
    db.session.commit()

    flash("Catégorie supprimée.", "info")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/edit-category/<int:category_id>", methods=["POST"])
@login_required
def edit_category(category_id):
    user_id = session.get("user_id")

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        flash("Catégorie introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    category.name = request.form.get("name", category.name)
    category.icon = request.form.get("icon", category.icon)
    category.color = request.form.get("color", category.color)

    budgets = Budget.query.filter_by(
        category_id=category.id,
        owner_id=user_id
    ).all()

    for budget in budgets:
        budget.category = category.name

    db.session.commit()

    flash("Catégorie modifiée.", "success")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session.get("user_id")

    name = request.form.get("name", "").strip()
    category_id = request.form.get("category_id")
    currency = request.form.get("currency", "EUR")

    if not name or not category_id:
        flash("Veuillez remplir tous les champs.", "danger")
        return redirect(url_for("budgets.index"))

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        flash("Catégorie introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    try:
        total_amount = float(request.form.get("total_amount", 0))
        spent_amount = float(request.form.get("spent_amount", 0))
        start_date = parse_date(request.form.get("start_date"))
        end_date = parse_date(request.form.get("end_date"))
    except ValueError:
        flash("Veuillez vérifier les montants et les dates.", "danger")
        return redirect(url_for("budgets.index"))

    if total_amount <= 0:
        flash("Le montant total doit être supérieur à 0.", "danger")
        return redirect(url_for("budgets.index"))

    current_monthly_budget, current_currency = get_current_monthly_budget(user_id)

    if current_monthly_budget > 0:
        monthly_budget_value = current_monthly_budget
        final_currency = current_currency
    else:
        monthly_budget_value = 0
        final_currency = currency

    new_budget = Budget(
        name=name,
        category=category.name,
        category_id=category.id,
        type="individual",
        monthly_budget=monthly_budget_value,
        total_amount=total_amount,
        spent_amount=spent_amount,
        remaining_amount=total_amount - spent_amount,
        currency=final_currency,
        start_date=start_date,
        end_date=end_date,
        period="Custom",
        owner_id=user_id,
        is_shared=False
    )

    db.session.add(new_budget)
    db.session.commit()

    flash("Budget créé avec succès.", "success")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/edit/<int:budget_id>", methods=["POST"])
@login_required
def edit(budget_id):
    user_id = session.get("user_id")

    budget = Budget.query.filter_by(
        id=budget_id,
        owner_id=user_id
    ).first()

    if not budget:
        flash("Budget introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    category_id = request.form.get("category_id")

    category = Category.query.filter_by(
        id=category_id,
        user_id=user_id
    ).first()

    if not category:
        flash("Catégorie introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    try:
        total_amount = float(request.form.get("total_amount", 0))
        spent_amount = float(request.form.get("spent_amount", 0))
        start_date = parse_date(request.form.get("start_date"))
        end_date = parse_date(request.form.get("end_date"))
    except ValueError:
        flash("Veuillez vérifier les montants et les dates.", "danger")
        return redirect(url_for("budgets.index"))

    if total_amount <= 0:
        flash("Le montant total doit être supérieur à 0.", "danger")
        return redirect(url_for("budgets.index"))

    budget.name = request.form.get("name", "").strip()
    budget.category = category.name
    budget.category_id = category.id
    budget.total_amount = total_amount
    budget.spent_amount = spent_amount
    budget.remaining_amount = total_amount - spent_amount
    budget.currency = request.form.get("currency", budget.currency)
    budget.start_date = start_date
    budget.end_date = end_date
    budget.period = "Custom"

    db.session.commit()

    flash("Budget modifié avec succès.", "success")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/delete/<int:budget_id>", methods=["POST"])
@login_required
def delete(budget_id):
    user_id = session.get("user_id")

    budget = Budget.query.filter_by(
        id=budget_id,
        owner_id=user_id
    ).first()

    if not budget:
        flash("Budget introuvable.", "danger")
        return redirect(url_for("budgets.index"))

    db.session.delete(budget)
    db.session.commit()

    flash("Budget supprimé.", "info")
    return redirect(url_for("budgets.index"))


@budget_bp.route("/adjust-monthly-budget", methods=["POST"])
@login_required
def adjust_monthly_budget():
    user_id = session.get("user_id")

    try:
        monthly_budget = float(request.form.get("monthly_budget", 0))
    except ValueError:
        flash("Monthly budget invalide.", "danger")
        return redirect(url_for("budgets.index"))

    currency = request.form.get("currency", "EUR")

    budgets = Budget.query.filter_by(
        owner_id=user_id,
        is_shared=False
    ).all()

    for budget in budgets:
        budget.monthly_budget = monthly_budget
        budget.currency = currency

    db.session.commit()

    flash("Monthly budget modifié avec succès.", "success")
    return redirect(url_for("budgets.index"))