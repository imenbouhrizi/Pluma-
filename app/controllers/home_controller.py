from flask import Blueprint, render_template, request, flash, redirect, url_for

home_bp = Blueprint("home", __name__)


# ---------------- HOME ----------------
@home_bp.route("/")
def index():
    return render_template("home.html")


# ---------------- ABOUT ----------------
@home_bp.route("/about")
def about():
    return render_template("about.html")


# ---------------- SERVICES ----------------
@home_bp.route("/services")
def services():
    return render_template("services.html")


# ---------------- PRICING ----------------
@home_bp.route("/pricing")
def pricing():
    plans = [
        {
            "name": "Starter Plan",
            "price": 49,
            "featured": False,
            "features": [
                "Get paid 3 days early",
                "Fee-Free Overdraft",
                "Detailed spend insights",
                "Priority Support",
            ],
        },
        {
            "name": "Enterprise Plan",
            "price": 99,
            "featured": True,
            "features": [
                "No Debit Card Fees",
                "Fee-Free Overdraft",
                "Detailed spend insights",
                "Priority Support",
                "Advanced Analytics",
                "Collaborative Finance",
            ],
        },
        {
            "name": "Pro Plan",
            "price": 139,
            "featured": False,
            "features": [
                "Get paid 3 days early",
                "Fee-Free Overdraft",
                "Detailed spend insights",
                "Priority Support",
            ],
        },
    ]
    return render_template("pricing.html", plans=plans)


# ---------------- CONTACT ----------------
@home_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in all fields.", "danger")
        else:
            # TODO: send email / save to DB here
            flash(f"Thank you {name}! Your message has been sent.", "success")
            return redirect(url_for("home.contact"))

    return render_template("contact.html")


# ---------------- SUBSCRIBE (AJAX-friendly) ----------------
@home_bp.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()
    if not email:
        flash("Please enter a valid email.", "danger")
    else:
        # TODO: save to newsletter list / send confirmation
        flash(f"{email} has been subscribed!", "success")
    return redirect(request.referrer or url_for("home.index"))