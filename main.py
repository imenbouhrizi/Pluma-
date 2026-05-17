from flask import Flask
from config.db import init_db
from routes.routes import register_routes
from app.controllers.auth_controller import google_bp, facebook_bp, mail
import os
from jinja2 import ChoiceLoader, FileSystemLoader

def create_app():
    app = Flask(__name__, template_folder=os.path.join("app", "views"), static_folder="static")

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join("app", "views")),
        FileSystemLoader(os.path.join("app", "templates"))
    ])

    # --- Configuration principale ---
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/pluma_budget'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Configuration SendGrid SMTP ---
    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'apikey'  # mot clé fixe pour SendGrid
    app.config['MAIL_PASSWORD'] = 'TA_CLE_API_SENDGRID'  # ta clé API SendGrid
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@tondomaine.com'

    # Initialisation DB et Mail
    init_db(app)
    mail.init_app(app)

    # Enregistrement des routes classiques
    register_routes(app)

    # Enregistrement des Blueprints OAuth
    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(facebook_bp, url_prefix="/login")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
