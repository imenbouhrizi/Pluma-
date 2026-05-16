from flask import Blueprint, render_template

# Définition du blueprint pour la gestion des utilisateurs
user_bp = Blueprint('users', __name__, url_prefix="/users")

@user_bp.route('/')
def index():
    # Affiche la page users.html
    return render_template("users.html")
