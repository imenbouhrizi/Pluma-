from flask import Flask
from config.db import init_db
from routes.routes import register_routes
from app.controllers.auth_controller import google_bp, facebook_bp, mail
from app.models.notification_model import Notification
import os
from jinja2 import ChoiceLoader, FileSystemLoader


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join("app", "views"),
        static_folder="static"
    )

    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join("app", "views")),
        FileSystemLoader(os.path.join("app", "templates"))
    ])

    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/pluma_budget'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'apikey'
    app.config['MAIL_PASSWORD'] = 'TA_CLE_API_SENDGRID'
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@tondomaine.com'

    init_db(app)
    mail.init_app(app)

    @app.context_processor
    def inject_notification_model():
        return dict(Notification=Notification)

    register_routes(app)

    app.register_blueprint(google_bp, url_prefix="/login")
    app.register_blueprint(facebook_bp, url_prefix="/login")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)