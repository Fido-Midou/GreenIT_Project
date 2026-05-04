"""Panneau d'administration : CRUD complet sur utilisateurs et annonces.

Accès restreint aux comptes role=admin (cf. decorators.admin_required).
"""
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
    session,
)
from sqlalchemy import desc, func
from .models import db, Utilisateur, Annonce
from .decorators import admin_required, get_current_user

bp = Blueprint("admin", __name__)


@bp.route("/")
@admin_required
def dashboard():
    """Tableau de bord : statistiques agrégées."""
    nb_users = db.session.query(func.count(Utilisateur.id)).scalar()
    nb_annonces = db.session.query(func.count(Annonce.id)).scalar()
    nb_dispos = (
        db.session.query(func.count(Annonce.id))
        .filter_by(statut="disponible")
        .scalar()
    )
    return render_template(
        "admin/dashboard.html",
        nb_users=nb_users,
        nb_annonces=nb_annonces,
        nb_dispos=nb_dispos,
    )


# ---- CRUD utilisateurs ----


@bp.route("/users")
@admin_required
def users_list():
    """Liste paginée des utilisateurs avec compteur d'annonces."""
    page = max(1, request.args.get("page", 1, type=int))
    per_page = current_app.config["ITEMS_PER_PAGE"]

    pagination = (
        Utilisateur.query.order_by(desc(Utilisateur.date_inscription))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "admin/users.html",
        users=pagination.items,
        pagination=pagination,
    )


@bp.route("/users/<int:user_id>/modifier", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    """Modification d'un utilisateur (admin peut changer le rôle)."""
    user = Utilisateur.query.get_or_404(user_id)

    if request.method == "POST":
        user.nom = request.form.get("nom", "").strip()
        user.prenom = request.form.get("prenom", "").strip()
        user.campus = request.form.get("campus", "").strip()
        role = request.form.get("role", "user")
        if role in ("user", "admin"):
            user.role = role
        db.session.commit()
        flash(f"Utilisateur {user.email} mis à jour.", "success")
        return redirect(url_for("admin.users_list"))

    return render_template("admin/user_edit.html", user=user)


@bp.route("/users/<int:user_id>/supprimer", methods=["POST"])
@admin_required
def delete_user(user_id):
    """Suppression d'un utilisateur (cascade sur annonces)."""
    current = get_current_user()
    if user_id == current.id:
        flash("Vous ne pouvez pas supprimer votre propre compte ici.", "error")
        return redirect(url_for("admin.users_list"))

    user = Utilisateur.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"Utilisateur {user.email} supprimé.", "success")
    return redirect(url_for("admin.users_list"))


# ---- CRUD annonces (vue admin) ----


@bp.route("/annonces")
@admin_required
def annonces_list():
    """Liste paginée de toutes les annonces (admin)."""
    page = max(1, request.args.get("page", 1, type=int))
    per_page = current_app.config["ITEMS_PER_PAGE"]

    pagination = (
        Annonce.query.order_by(desc(Annonce.date_publication))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "admin/annonces.html",
        annonces=pagination.items,
        pagination=pagination,
    )


@bp.route("/annonces/<int:annonce_id>/supprimer", methods=["POST"])
@admin_required
def delete_annonce(annonce_id):
    """Suppression d'une annonce par un admin."""
    annonce = Annonce.query.get_or_404(annonce_id)
    db.session.delete(annonce)
    db.session.commit()
    flash("Annonce supprimée.", "success")
    return redirect(url_for("admin.annonces_list"))
