import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

from config.db import db
from app.models.user_model import User

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@settings_bp.route("/", methods=["GET", "POST"])
def index():

    # ================= CHECK LOGIN =================
    user_id = session.get("user_id")
    if not user_id:
        flash("Veuillez vous connecter.", "warning")
        return redirect(url_for("auth.login"))

    # ================= GET USER =================
    user = User.query.get(user_id)
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for("auth.login"))

    # ================= UPDATE PROFILE =================
    if request.method == "POST":
        try:
            user.name = request.form.get("name")
            user.username = request.form.get("username")
            user.email = request.form.get("email")
            user.date_of_birth = request.form.get("dob")
            user.address = request.form.get("address")
            user.country = request.form.get("country")
            user.city = request.form.get("city")

            # ================= IMAGE UPLOAD =================
            file = request.files.get("avatar")

            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                user.avatar = filename

            db.session.commit()

            flash("✅ Profil mis à jour avec succès.", "success")
            return redirect(url_for("settings.index"))

        except Exception:
            db.session.rollback()
            flash("❌ Erreur lors de la mise à jour.", "danger")

    return render_template("settings.html", user=user)