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
# --------------------------------------------------------------------------------------------------
# REMARQUE :
# Pour cette version, nous changeons la base SQLite locale (pluma.db) vers MySQL XAMPP
# Base utilisée : pluma_budget
# 
# Avant :
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pluma.db'
#
# Après :
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/pluma_budget'
#
# ✅ Chaque membre du groupe doit créer localement la même base MySQL : pluma_budget
# ✅ N'oubliez pas d'installer le driver MySQL pour Python : pip install pymysql
# ✅ Assurez-vous que Apache + MySQL sont lancés dans XAMPP avant de démarrer Flask

# --------------------------------------------------------------------------------------------------
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/pluma_budget'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
