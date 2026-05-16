from flask import Flask
from config.db import init_db
from routes.routes import register_routes
import os
from jinja2 import ChoiceLoader, FileSystemLoader

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join("app", "views"),   # pages
        static_folder="static"
    )

    # Ajout de app/templates pour les layouts
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(os.path.join("app", "views")),
        FileSystemLoader(os.path.join("app", "templates"))
    ])

    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pluma.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
