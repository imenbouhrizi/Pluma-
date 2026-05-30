from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from config.db import db
from app.utils.auth import login_required
from app.models.user_model import User
from app.models.category_model import Category
from app.models.notification_model import Notification
from app.models.shared_budget_model import SharedBudgetExpense
from app.models.shared_budget_model import (
    SharedBudget,
    SharedBudgetCategory,
    SharedBudgetMember,
    SharedBudgetInvitation,
    SharedBudgetExpense
)

shared_budget_bp = Blueprint("shared_budgets", __name__)


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def is_admin(shared_budget_id, user_id):
    return SharedBudgetMember.query.filter_by(
        shared_budget_id=shared_budget_id,
        user_id=user_id,
        role="admin",
        status="accepted"
    ).first() is not None


@shared_budget_bp.route("/budgets/shared")
@login_required
def index():
    user_id = session.get("user_id")
    open_members = request.args.get("open_members")

    memberships = SharedBudgetMember.query.filter_by(
        user_id=user_id,
        status="accepted"
    ).all()

    shared_budgets = [
        {
            "shared_budget": member.shared_budget,
            "role": member.role
        }
        for member in memberships
    ]

    categories = Category.query.filter_by(
        user_id=user_id
    ).order_by(Category.name.asc()).all()

    return render_template(
        "shared_budgets.html",
        shared_budgets=shared_budgets,
        categories=categories,
        open_members=open_members,
        SharedBudgetExpense=SharedBudgetExpense

    )


@shared_budget_bp.route("/budgets/shared/create", methods=["POST"])
@login_required
def create():
    user_id = session.get("user_id")

    name = request.form.get("name", "").strip()
    currency = request.form.get("currency", "EUR")
    category_ids = request.form.getlist("category_ids")
    emails = request.form.get("emails", "")

    try:
        total_amount = float(request.form.get("total_amount", 0))
        start_date = parse_date(request.form.get("start_date"))
        end_date = parse_date(request.form.get("end_date"))
    except ValueError:
        flash("Veuillez vérifier le montant et les dates.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not name or total_amount <= 0:
        flash("Veuillez remplir correctement les champs.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget(
        name=name,
        total_amount=total_amount,
        spent_amount=0,
        remaining_amount=total_amount,
        currency=currency,
        start_date=start_date,
        end_date=end_date,
        creator_id=user_id
    )

    db.session.add(shared_budget)
    db.session.flush()

    db.session.add(
        SharedBudgetMember(
            shared_budget_id=shared_budget.id,
            user_id=user_id,
            role="admin",
            status="accepted"
        )
    )

    for category_id in category_ids:
        db.session.add(
            SharedBudgetCategory(
                shared_budget_id=shared_budget.id,
                category_id=int(category_id)
            )
        )

    email_list = [
        email.strip()
        for email in emails.replace("\n", ",").split(",")
        if email.strip()
    ]

    for email in email_list:
        invited_user = User.query.filter_by(email=email).first()

        if invited_user and invited_user.id != user_id:
            already_member = SharedBudgetMember.query.filter_by(
                shared_budget_id=shared_budget.id,
                user_id=invited_user.id,
                status="accepted"
            ).first()

            if not already_member:
                old_invitations = SharedBudgetInvitation.query.filter_by(
                    shared_budget_id=shared_budget.id,
                    invited_user_id=invited_user.id
                ).all()

                for old in old_invitations:
                    db.session.delete(old)

                db.session.flush()

                invitation = SharedBudgetInvitation(
                    shared_budget_id=shared_budget.id,
                    invited_user_id=invited_user.id,
                    invited_by_id=user_id,
                    status="pending"
                )

                db.session.add(invitation)
                db.session.flush()

                notification = Notification(
                    user_id=invited_user.id,
                    title="Invitation budget partagé",
                    message=f"Vous avez reçu une invitation pour rejoindre le budget partagé : {shared_budget.name}",
                    type="shared_budget_invitation",
                    related_id=invitation.id
                )

                db.session.add(notification)

    db.session.commit()

    flash("Budget partagé créé. Invitations envoyées.", "success")
    return redirect(url_for("shared_budgets.index", open_members=shared_budget.id))


@shared_budget_bp.route("/budgets/shared/invite/<int:shared_budget_id>", methods=["POST"])
@login_required
def invite_member(shared_budget_id):
    user_id = session.get("user_id")

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    emails = request.form.get("emails", "")

    email_list = [
        email.strip()
        for email in emails.replace("\n", ",").split(",")
        if email.strip()
    ]

    for email in email_list:
        invited_user = User.query.filter_by(email=email).first()

        if invited_user and invited_user.id != user_id:
            already_member = SharedBudgetMember.query.filter_by(
                shared_budget_id=shared_budget_id,
                user_id=invited_user.id,
                status="accepted"
            ).first()

            if not already_member:
                old_invitations = SharedBudgetInvitation.query.filter_by(
                    shared_budget_id=shared_budget_id,
                    invited_user_id=invited_user.id
                ).all()

                for old in old_invitations:
                    db.session.delete(old)

                db.session.flush()

                invitation = SharedBudgetInvitation(
                    shared_budget_id=shared_budget_id,
                    invited_user_id=invited_user.id,
                    invited_by_id=user_id,
                    status="pending"
                )

                db.session.add(invitation)
                db.session.flush()

                notification = Notification(
                    user_id=invited_user.id,
                    title="Invitation budget partagé",
                    message=f"Vous avez reçu une invitation pour rejoindre le budget partagé : {shared_budget.name}",
                    type="shared_budget_invitation",
                    related_id=invitation.id
                )

                db.session.add(notification)

    db.session.commit()

    flash("Invitation envoyée.", "success")
    return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))


@shared_budget_bp.route("/budgets/shared/change-role/<int:member_id>", methods=["POST"])
@login_required
def change_role(member_id):
    user_id = session.get("user_id")

    member = SharedBudgetMember.query.get(member_id)

    if not member:
        flash("Membre introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not is_admin(member.shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index", open_members=member.shared_budget_id))

    shared_budget = SharedBudget.query.get(member.shared_budget_id)

    if shared_budget and member.user_id == shared_budget.creator_id:
        flash("Le créateur du budget reste admin.", "info")
        return redirect(url_for("shared_budgets.index", open_members=member.shared_budget_id))

    member.role = request.form.get("role", "user")
    db.session.commit()

    flash("Rôle modifié.", "success")
    return redirect(url_for("shared_budgets.index", open_members=member.shared_budget_id))


@shared_budget_bp.route("/budgets/shared/remove-member/<int:member_id>", methods=["POST"])
@login_required
def remove_member(member_id):
    user_id = session.get("user_id")

    member = SharedBudgetMember.query.get(member_id)

    if not member:
        flash("Membre introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget_id = member.shared_budget_id

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))

    shared_budget = SharedBudget.query.get(shared_budget_id)

    if shared_budget and member.user_id == shared_budget.creator_id:
        flash("Impossible de supprimer le créateur du budget.", "danger")
        return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))

    db.session.delete(member)
    db.session.commit()

    flash("Membre supprimé.", "info")
    return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))


@shared_budget_bp.route("/budgets/shared/cancel-invitation/<int:invitation_id>", methods=["POST"])
@login_required
def cancel_invitation(invitation_id):
    user_id = session.get("user_id")

    invitation = SharedBudgetInvitation.query.get(invitation_id)

    if not invitation:
        flash("Invitation introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget_id = invitation.shared_budget_id

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))

    notification = Notification.query.filter_by(
        related_id=invitation.id,
        type="shared_budget_invitation"
    ).first()

    if notification:
        db.session.delete(notification)

    db.session.delete(invitation)
    db.session.commit()

    flash("Invitation annulée.", "info")
    return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))


@shared_budget_bp.route("/budgets/shared/delete/<int:shared_budget_id>", methods=["POST"])
@login_required
def delete(shared_budget_id):
    user_id = session.get("user_id")

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    db.session.delete(shared_budget)
    db.session.commit()

    flash("Budget partagé supprimé.", "info")
    return redirect(url_for("shared_budgets.index"))


@shared_budget_bp.route("/budgets/shared/edit/<int:shared_budget_id>", methods=["POST"])
@login_required
def edit(shared_budget_id):
    user_id = session.get("user_id")

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    try:
        shared_budget.total_amount = float(request.form.get("total_amount", 0))
        shared_budget.start_date = parse_date(request.form.get("start_date"))
        shared_budget.end_date = parse_date(request.form.get("end_date"))
    except ValueError:
        flash("Veuillez vérifier les données.", "danger")
        return redirect(url_for("shared_budgets.index", open_members=shared_budget_id))

    shared_budget.name = request.form.get("name", "").strip()
    shared_budget.currency = request.form.get("currency", "EUR")
    shared_budget.remaining_amount = shared_budget.total_amount - shared_budget.spent_amount

    SharedBudgetCategory.query.filter_by(
        shared_budget_id=shared_budget.id
    ).delete()

    category_ids = request.form.getlist("category_ids")

    for category_id in category_ids:
        db.session.add(
            SharedBudgetCategory(
                shared_budget_id=shared_budget.id,
                category_id=int(category_id)
            )
        )

    db.session.commit()

    flash("Budget partagé modifié.", "success")
    return redirect(url_for("shared_budgets.index"))

@shared_budget_bp.route("/budgets/shared/view/<int:shared_budget_id>")
@login_required
def view(shared_budget_id):

    user_id = session.get("user_id")

    member = SharedBudgetMember.query.filter_by(
        shared_budget_id=shared_budget_id,
        user_id=user_id,
        status="accepted"
    ).first()

    if not member:
        flash("Accès refusé.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get_or_404(shared_budget_id)

    expenses = SharedBudgetExpense.query.filter_by(
        shared_budget_id=shared_budget_id
    ).order_by(
        SharedBudgetExpense.created_at.desc()
    ).all()

    return render_template(
        "shared_budget_view.html",
        shared_budget=shared_budget,
        expenses=expenses,
        user_role=member.role
    )

@shared_budget_bp.route("/budgets/shared/add-expense/<int:shared_budget_id>", methods=["POST"])
@login_required
def add_expense(shared_budget_id):
    user_id = session.get("user_id")

    if not is_admin(shared_budget_id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    name = request.form.get("name", "").strip()
    category_id = request.form.get("category_id")

    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        flash("Montant invalide.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not name or not category_id or amount <= 0:
        flash("Veuillez remplir correctement la dépense.", "danger")
        return redirect(url_for("shared_budgets.index"))

    expense = SharedBudgetExpense(
        shared_budget_id=shared_budget.id,
        category_id=int(category_id),
        added_by_id=user_id,
        name=name,
        amount=amount
    )

    db.session.add(expense)

    shared_budget.spent_amount += amount
    shared_budget.remaining_amount = (
        shared_budget.total_amount - shared_budget.spent_amount
    )

    if shared_budget.spent_amount > shared_budget.total_amount:
        exceeded_amount = shared_budget.spent_amount - shared_budget.total_amount

        members = SharedBudgetMember.query.filter_by(
            shared_budget_id=shared_budget.id,
            status="accepted"
        ).all()

        for member in members:
            db.session.add(
                Notification(
                    user_id=member.user_id,
                    title="Budget dépassé",
                    message=(
                        f"Le budget partagé '{shared_budget.name}' "
                        f"a dépassé sa limite de "
                        f"{exceeded_amount:.2f} {shared_budget.currency}."
                    ),
                    type="budget_exceeded"
                )
            )

    db.session.commit()

    flash("Dépense ajoutée.", "success")
    return redirect(url_for("shared_budgets.index"))

@shared_budget_bp.route("/budgets/shared/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    user_id = session.get("user_id")

    expense = SharedBudgetExpense.query.get(expense_id)

    if not expense:
        flash("Dépense introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(expense.shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not is_admin(shared_budget.id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget.spent_amount -= expense.amount
    shared_budget.remaining_amount = shared_budget.total_amount - shared_budget.spent_amount

    db.session.delete(expense)
    db.session.commit()

    flash("Dépense supprimée.", "info")
    return redirect(url_for("shared_budgets.index"))

@shared_budget_bp.route("/budgets/shared/edit-expense/<int:expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    user_id = session.get("user_id")

    expense = SharedBudgetExpense.query.get(expense_id)

    if not expense:
        flash("Dépense introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    shared_budget = SharedBudget.query.get(expense.shared_budget_id)

    if not shared_budget:
        flash("Budget partagé introuvable.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not is_admin(shared_budget.id, user_id):
        flash("Action non autorisée.", "danger")
        return redirect(url_for("shared_budgets.index"))

    name = request.form.get("name", "").strip()
    category_id = request.form.get("category_id")

    try:
        new_amount = float(request.form.get("amount", 0))
    except ValueError:
        flash("Montant invalide.", "danger")
        return redirect(url_for("shared_budgets.index"))

    if not name or not category_id or new_amount <= 0:
        flash("Veuillez remplir correctement la dépense.", "danger")
        return redirect(url_for("shared_budgets.index"))

    old_amount = expense.amount

    expense.name = name
    expense.category_id = int(category_id)
    expense.amount = new_amount

    shared_budget.spent_amount = shared_budget.spent_amount - old_amount + new_amount
    shared_budget.remaining_amount = shared_budget.total_amount - shared_budget.spent_amount

    db.session.commit()

    flash("Dépense modifiée.", "success")
    return redirect(url_for("shared_budgets.index"))