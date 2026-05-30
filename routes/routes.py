# routes/routes.py

# Import des Blueprints depuis les contrôleurs
from app.controllers.home_controller import home_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.dashboard_controller import dashboard_bp
from app.controllers.transaction_controller import transaction_bp
from app.controllers.budget_controller import budget_bp
from app.controllers.shared_budget_controller import shared_budget_bp
from app.controllers.notification_controller import notification_bp
from app.controllers.goal_controller import goal_bp   # ⚠️ doit exister dans goal_controller.py
from app.controllers.settings_controller import settings_bp
from app.controllers.user_controller import user_bp

def register_routes(app):
    """
    Fonction qui enregistre tous les Blueprints de l'application.
    Chaque contrôleur est associé à un préfixe d'URL pour garder une structure claire.
    """

    # Page d'accueil
    app.register_blueprint(home_bp, url_prefix="/")

    # Authentification (login, signup, logout)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Tableau de bord
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    # Transactions
    app.register_blueprint(transaction_bp, url_prefix="/transactions")

    # Budgets
    app.register_blueprint(budget_bp, url_prefix="/budgets")
    app.register_blueprint(shared_budget_bp)
    app.register_blueprint(notification_bp)

    # Objectifs financiers
    app.register_blueprint(goal_bp, url_prefix="/goals")

    # Paramètres utilisateur
    app.register_blueprint(settings_bp, url_prefix="/settings")

    # Gestion des utilisateurs (admin)
    app.register_blueprint(user_bp, url_prefix="/users")
