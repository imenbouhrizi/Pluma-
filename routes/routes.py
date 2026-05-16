# routes/routes.py

# Import des blueprints depuis les contrôleurs
from app.controllers.home_controller import home_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.transaction_controller import transaction_bp
from app.controllers.budget_controller import budget_bp
from app.controllers.goal_controller import goal_bp
from app.controllers.settings_controller import settings_bp
from app.controllers.user_controller import user_bp

def register_routes(app):
    """
    Fonction qui enregistre tous les blueprints de l'application.
    Chaque contrôleur est associé à un préfixe d'URL pour garder une structure claire.
    """
    app.register_blueprint(home_bp)  # Page d'accueil
    app.register_blueprint(auth_bp, url_prefix="/auth")  # Login / Signup
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")  # Tableau de bord
    app.register_blueprint(transaction_bp, url_prefix="/transactions")  # Transactions
    app.register_blueprint(budget_bp, url_prefix="/budgets")  # Budgets
    app.register_blueprint(goal_bp, url_prefix="/goals")  # Objectifs
    app.register_blueprint(settings_bp, url_prefix="/settings")  # Paramètres
    app.register_blueprint(user_bp, url_prefix="/users")  # Gestion des utilisateurs
