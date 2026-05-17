from flask import Blueprint, render_template
from app.utils.auth import login_required

goal_bp = Blueprint('goals', __name__)

@goal_bp.route('/')
@login_required
def index():
    return render_template('goals.html')