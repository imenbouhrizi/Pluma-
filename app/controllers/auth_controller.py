from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import secrets

from config.db import db
from app.models.user_model import User

# --- Blueprint principal ---
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# --- OAuth Blueprints ---
google_bp = make_google_blueprint(
    client_id="TON_GOOGLE_CLIENT_ID",
    client_secret="TON_GOOGLE_CLIENT_SECRET",
    scope=["profile", "email"],
    redirect_to="auth.google_login"
)

facebook_bp = make_facebook_blueprint(
    client_id="TON_FACEBOOK_APP_ID",
    client_secret="TON_FACEBOOK_APP_SECRET",
    scope=["email"],
    redirect_to="auth.facebook_login"
)

# --- Mail & Token ---
mail = Mail()
serializer = URLSafeTimedSerializer("supersecretkey")

# ------------------- ROUTES -------------------

# --- Login classique ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user"] = user.email
            session["role"] = user.role
            session["token"] = secrets.token_hex(16)
            flash("Connexion réussie !", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template("login.html")

# --- Signup classique ---
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        name = email.split("@")[0]

        if User.query.filter_by(email=email).first():
            flash("Un compte existe déjà avec cet email.", "warning")
            return redirect(url_for("auth.login"))

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for("auth.signup"))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Compte créé avec succès !", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

# --- Logout ---
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))

# --- Google OAuth Callback ---
@auth_bp.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Erreur Google.", "danger")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = info["email"]
    name = info.get("name", email.split("@")[0])

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, password=generate_password_hash("oauth"), role="user")
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["user"] = user.email
    session["role"] = user.role
    flash("Connexion réussie avec Google !", "success")
    return redirect(url_for("dashboard.index"))

# --- Facebook OAuth Callback ---
@auth_bp.route("/facebook_login")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))

    resp = facebook.get("/me?fields=id,name,email")
    if not resp.ok:
        flash("Erreur Facebook.", "danger")
        return redirect(url_for("auth.login"))

    info = resp.json()
    email = info.get("email")
    name = info.get("name")

    if not email:
        flash("Impossible de récupérer l'email depuis Facebook.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email, password=generate_password_hash("oauth"), role="user")
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["user"] = user.email
    session["role"] = user.role
    flash("Connexion réussie avec Facebook !", "success")
    return redirect(url_for("dashboard.index"))

# --- Mot de passe oublié ---
@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            try:
                token = serializer.dumps(email, salt="password-reset")
                reset_url = url_for("auth.reset_password", token=token, _external=True)

                msg = Message("Réinitialisation de mot de passe",
                              sender="noreply@tondomaine.com",
                              recipients=[email])
                msg.body = f"Bonjour,\n\nCliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}\n\nCe lien expire dans 30 minutes."
                mail.send(msg)

                flash("✅ Email envoyé avec succès ! Vérifiez votre boîte de réception.", "success")
                return redirect(url_for("auth.login"))
            except Exception:
                flash("❌ Une erreur est survenue lors de l'envoi de l'email.", "danger")
                return redirect(url_for("auth.forgot_password"))
        else:
            flash("⚠️ Aucun compte trouvé avec cet email.", "warning")

    return render_template("forgot_password.html")

# --- Réinitialisation du mot de passe ---
@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)
    except (SignatureExpired, BadSignature):
        flash("Lien invalide ou expiré.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash("Mot de passe réinitialisé avec succès !", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)