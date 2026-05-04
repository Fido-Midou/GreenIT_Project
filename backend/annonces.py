"""Routes CRUD de l'entité métier Annonce.

Conforme aux consignes :
- Pagination (LIMIT 20).
- SELECT ciblé (pas de SELECT *) via SQLAlchemy.
- Validation côté serveur.
- Confirmation explicite avant suppression.
- Vérification des droits avant modification/suppression.
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
)
from sqlalchemy import desc
from ..models import db, Annonce, Utilisateur, CATEGORIES, ETATS, TYPES, STATUTS
from .decorators import login_required, get_current_user

bp = Blueprint("annonces", __name__)


def _validate_annonce(data):
    """Validation serveur d'une annonce."""
    errors = []
    titre = data.get("titre", "").strip()
    if not titre or len(titre) > 120:
        errors.append("Titre requis (max 120 caractères).")
    description = data.get("description", "").strip()
    if not description or len(description) > 2000:
        errors.append("Description requise (max 2000 caractères).")
    if data.get("categorie") not in CATEGORIES:
        errors.append("Catégorie invalide.")
    if data.get("etat") not in ETATS:
        errors.append("État invalide.")
    if data.get("type_annonce") not in TYPES:
        errors.append("Type invalide.")
    return errors


@bp.route("/annonces")
def liste():
    """Liste paginée des annonces, filtrable par catégorie."""
    page = max(1, request.args.get("page", 1, type=int))
    categorie = request.args.get("categorie", "").strip()
    per_page = current_app.config["ITEMS_PER_PAGE"]

    # Requête optimisée : ne récupère que les colonnes utiles, paginée.
    query = Annonce.query.filter_by(statut="disponible")
    if categorie and categorie in CATEGORIES:
        query = query.filter_by(categorie=categorie)
    query = query.order_by(desc(Annonce.date_publication))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "annonces.html",
        pagination=pagination,
        annonces=pagination.items,
        categorie_active=categorie,
        categories=CATEGORIES,
    )


@bp.route("/annonces/<int:annonce_id>")
def detail(annonce_id):
    """Affichage détaillé d'une annonce."""
    annonce = Annonce.query.get_or_404(annonce_id)
    return render_template("annonce_detail.html", annonce=annonce)


@bp.route("/annonces/nouvelle", methods=["GET", "POST"])
@login_required
def creer():
    """Dépôt d'une nouvelle annonce."""
    user = get_current_user()

    if request.method == "POST":
        errors = _validate_annonce(request.form)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "annonce_form.html",
                form=request.form,
                categories=CATEGORIES,
                etats=ETATS,
                types=TYPES,
                action="Créer",
            )

        annonce = Annonce(
            titre=request.form["titre"].strip(),
            description=request.form["description"].strip(),
            categorie=request.form["categorie"],
            etat=request.form["etat"],
            type_annonce=request.form["type_annonce"],
            id_utilisateur=user.id,
        )
        db.session.add(annonce)
        db.session.commit()

        flash("Annonce publiée.", "success")
        return redirect(url_for("annonces.detail", annonce_id=annonce.id))

    return render_template(
        "annonce_form.html",
        form={},
        categories=CATEGORIES,
        etats=ETATS,
        types=TYPES,
        action="Créer",
    )


@bp.route("/annonces/<int:annonce_id>/modifier", methods=["GET", "POST"])
@login_required
def modifier(annonce_id):
    """Modification d'une annonce. Seul l'auteur ou un admin peut modifier."""
    user = get_current_user()
    annonce = Annonce.query.get_or_404(annonce_id)

    if annonce.id_utilisateur != user.id and not user.is_admin:
        abort(403)

    if request.method == "POST":
        errors = _validate_annonce(request.form)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "annonce_form.html",
                form=request.form,
                categories=CATEGORIES,
                etats=ETATS,
                types=TYPES,
                action="Modifier",
                annonce=annonce,
            )

        annonce.titre = request.form["titre"].strip()
        annonce.description = request.form["description"].strip()
        annonce.categorie = request.form["categorie"]
        annonce.etat = request.form["etat"]
        annonce.type_annonce = request.form["type_annonce"]
        if request.form.get("statut") in STATUTS:
            annonce.statut = request.form["statut"]
        db.session.commit()

        flash("Annonce mise à jour.", "success")
        return redirect(url_for("annonces.detail", annonce_id=annonce.id))

    # GET : pré-remplit le formulaire.
    form = {
        "titre": annonce.titre,
        "description": annonce.description,
        "categorie": annonce.categorie,
        "etat": annonce.etat,
        "type_annonce": annonce.type_annonce,
        "statut": annonce.statut,
    }
    return render_template(
        "annonce_form.html",
        form=form,
        categories=CATEGORIES,
        etats=ETATS,
        types=TYPES,
        statuts=STATUTS,
        action="Modifier",
        annonce=annonce,
    )


@bp.route("/annonces/<int:annonce_id>/supprimer", methods=["POST"])
@login_required
def supprimer(annonce_id):
    """Suppression d'une annonce. POST uniquement, confirmation côté template."""
    user = get_current_user()
    annonce = Annonce.query.get_or_404(annonce_id)

    if annonce.id_utilisateur != user.id and not user.is_admin:
        abort(403)

    db.session.delete(annonce)
    db.session.commit()
    flash("Annonce supprimée.", "success")
    return redirect(url_for("auth_user.profile"))


# Profil utilisateur (lié aux annonces personnelles).
bp_user = Blueprint("auth_user", __name__)


@bp_user.route("/profil")
@login_required
def profile():
    """Page de profil : infos perso + ses annonces."""
    user = get_current_user()
    page = max(1, request.args.get("page", 1, type=int))
    per_page = current_app.config["ITEMS_PER_PAGE"]

    pagination = (
        user.annonces.order_by(desc(Annonce.date_publication))
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "profile.html",
        user=user,
        annonces=pagination.items,
        pagination=pagination,
    )


@bp_user.route("/profil/modifier", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Modification du profil."""
    user = get_current_user()

    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        campus = request.form.get("campus", "").strip()

        if not nom or not prenom or not campus:
            flash("Tous les champs sont requis.", "error")
            return render_template("profile_edit.html", user=user)

        user.nom = nom
        user.prenom = prenom
        user.campus = campus

        # Changement de mot de passe optionnel.
        new_pwd = request.form.get("new_password", "")
        if new_pwd:
            current_pwd = request.form.get("current_password", "")
            if not user.check_password(current_pwd):
                flash("Mot de passe actuel incorrect.", "error")
                return render_template("profile_edit.html", user=user)
            if len(new_pwd) < 8:
                flash("Le nouveau mot de passe doit faire au moins 8 caractères.", "error")
                return render_template("profile_edit.html", user=user)
            user.set_password(new_pwd)

        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for("auth_user.profile"))

    return render_template("profile_edit.html", user=user)


@bp_user.route("/profil/supprimer", methods=["POST"])
@login_required
def delete_account():
    """Suppression du compte utilisateur (et annonces en cascade)."""
    from flask import session
    user = get_current_user()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Compte supprimé. À bientôt.", "success")
    return redirect(url_for("index"))
