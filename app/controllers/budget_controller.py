from flask import Blueprint, render_template
from app.utils.auth import login_required

budget_bp = Blueprint('budgets', __name__)

@budget_bp.route('/')
@login_required
def index():
    return render_template('budgets.html')