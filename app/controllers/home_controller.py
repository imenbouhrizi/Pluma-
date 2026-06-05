from flask import Blueprint, render_template, request, flash, redirect, url_for

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template("home.html")


@home_bp.route("/about")
def about():
    return render_template("home.html")


@home_bp.route("/services")
def services():
    return render_template("home.html")


@home_bp.route("/pricing")
def pricing():
    return render_template("home.html")


@home_bp.route("/contact", methods=["POST"])
def contact():
    email = request.form.get("email", "").strip()

    if not email:
        flash("Please enter your email.", "danger")
    else:
        flash("Thank you for subscribing!", "success")

    return redirect(url_for("home.index"))


@home_bp.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()

    if not email:
        flash("Please enter a valid email.", "danger")
    else:
        flash(f"{email} has been subscribed!", "success")

    return redirect(url_for("home.index"))