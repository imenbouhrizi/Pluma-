from flask import Blueprint, redirect, url_for, flash, session, request
from config.db import db
from app.utils.auth import login_required

from app.models.notification_model import Notification

from app.models.shared_budget_model import (
    SharedBudgetInvitation,
    SharedBudgetMember
)

notification_bp = Blueprint("notifications", __name__)


@notification_bp.route(
    "/notifications/accept/<int:notification_id>",
    methods=["POST"]
)
@login_required
def accept_invitation(notification_id):

    user_id = session.get("user_id")

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()

    if not notification:
        flash("Notification introuvable.", "danger")
        return redirect(request.referrer or "/")

    invitation = SharedBudgetInvitation.query.get(
        notification.related_id
    )

    if not invitation:
        flash("Invitation introuvable.", "danger")
        return redirect(request.referrer or "/")

    invitation.status = "accepted"

    existing_member = SharedBudgetMember.query.filter_by(
        shared_budget_id=invitation.shared_budget_id,
        user_id=user_id
    ).first()

    if not existing_member:

        member = SharedBudgetMember(
            shared_budget_id=invitation.shared_budget_id,
            user_id=user_id,
            role="user",
            status="accepted"
        )

        db.session.add(member)

        SharedBudgetInvitation.query.filter_by(
            shared_budget_id=invitation.shared_budget_id,
            invited_user_id=user_id
        ).delete()

        db.session.commit()

        notification.is_read = True

        db.session.commit()

    flash("Invitation acceptée.", "success")

    return redirect(url_for("shared_budgets.index"))


@notification_bp.route(
    "/notifications/refuse/<int:notification_id>",
    methods=["POST"]
)
@login_required
def refuse_invitation(notification_id):

    user_id = session.get("user_id")

    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=user_id
    ).first()

    if not notification:
        flash("Notification introuvable.", "danger")
        return redirect(request.referrer or "/")

    invitation = SharedBudgetInvitation.query.get(
        notification.related_id
    )

    if invitation:
        invitation.status = "refused"

    notification.is_read = True

    db.session.commit()

    flash("Invitation refusée.", "info")

    return redirect(request.referrer or "/")

@notification_bp.route("/notifications/mark-as-read", methods=["POST"])
@login_required
def mark_as_read():

    user_id = session.get("user_id")

    Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).update({
        "is_read": True
    })

    db.session.commit()

    return {"success": True}