from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import login_required

transaction_bp = Blueprint('transactions', __name__, url_prefix="/transactions")

# Exemple de données en mémoire (remplace par DB MySQL/SQLAlchemy)
transactions = [
    {"id": 1, "date": "2026-05-15", "description": "Supermarché", "amount": -50, "type": "Dépense", "category": "Alimentation"},
    {"id": 2, "date": "2026-05-14", "description": "Salaire", "amount": 1500, "type": "Revenu", "category": "Travail"}
]

# --- LISTE ---
@transaction_bp.route('/')
@login_required
def index():
    return render_template("transactions.html", transactions=transactions)

# --- AJOUT ---
@transaction_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        new_id = max([t["id"] for t in transactions], default=0) + 1
        date = request.form.get('date')
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        type_ = request.form.get('type')
        category = request.form.get('category')

        transactions.append({
            "id": new_id,
            "date": date,
            "description": description,
            "amount": amount,
            "type": type_,
            "category": category
        })
        flash("Transaction ajoutée avec succès !", "success")
        return redirect(url_for('transactions.index'))

    return render_template("add_transaction.html")

# --- MODIFICATION ---
@transaction_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    transaction = next((t for t in transactions if t["id"] == transaction_id), None)
    if not transaction:
        flash("Transaction introuvable.", "danger")
        return redirect(url_for('transactions.index'))

    if request.method == 'POST':
        transaction["date"] = request.form.get('date')
        transaction["description"] = request.form.get('description')
        transaction["amount"] = float(request.form.get('amount'))
        transaction["type"] = request.form.get('type')
        transaction["category"] = request.form.get('category')
        flash("Transaction modifiée avec succès !", "success")
        return redirect(url_for('transactions.index'))

    return render_template("edit_transaction.html", transaction=transaction)

# --- SUPPRESSION ---
@transaction_bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete(transaction_id):
    global transactions
    transactions = [t for t in transactions if t["id"] != transaction_id]
    flash("Transaction supprimée.", "info")
    return redirect(url_for('transactions.index'))
