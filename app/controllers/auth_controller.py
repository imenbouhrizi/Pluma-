from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

# Exemple de "base de données" en mémoire (remplace par SQLAlchemy/MySQL)
users_db = {}

# --- LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = users_db.get(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user'] = email
            session['token'] = secrets.token_hex(16)  # token unique
            flash("Connexion réussie !", "success")
            return redirect(url_for('dashboard.index'))
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template("login.html")

# --- SIGNUP ---
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if email in users_db:
            flash("Un compte existe déjà avec cet email.", "warning")
            return redirect(url_for('auth.login'))

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
        else:
            users_db[email] = {
                "username": username,
                "password_hash": generate_password_hash(password)
            }
            flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
            return redirect(url_for('auth.login'))

    return render_template("signup.html")

# --- LOGOUT ---
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('auth.login'))
