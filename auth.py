"""Routes d'authentification : inscription, connexion, déconnexion.

Sécurité :
- Mots de passe hashés avec bcrypt (cf. models.set_password).
- Validation côté serveur (format email, longueur du mot de passe).
- Sessions Flask signées (SECRET_KEY).
- Requêtes paramétrées (via SQLAlchemy ORM).
"""
import re
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from .models import db, Utilisateur

bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[\w\.\-+]+@[\w\-]+(\.[\w\-]+)+$")
MIN_PASSWORD_LENGTH = 8


def _validate_registration(data):
    """Retourne une liste d'erreurs de validation."""
    errors = []
    if not data.get("nom", "").strip():
        errors.append("Le nom est requis.")
    if not data.get("prenom", "").strip():
        errors.append("Le prénom est requis.")
    email = data.get("email", "").strip().lower()
    if not email or not EMAIL_REGEX.match(email):
        errors.append("Adresse email invalide.")
    if not data.get("campus", "").strip():
        errors.append("Le campus est requis.")
    pwd = data.get("password", "")
    if len(pwd) < MIN_PASSWORD_LENGTH:
        errors.append(
            f"Le mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères."
        )
    if pwd != data.get("password_confirm", ""):
        errors.append("Les deux mots de passe ne correspondent pas.")
    return errors


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Création d'un compte utilisateur."""
    if "user_id" in session:
        return redirect(url_for("annonces.liste"))

    if request.method == "POST":
        errors = _validate_registration(request.form)
        email = request.form.get("email", "").strip().lower()

        # Vérifie l'unicité de l'email.
        if not errors and Utilisateur.query.filter_by(email=email).first():
            errors.append("Un compte existe déjà avec cet email.")

        if errors:
            for e in errors:
                flash(e, "error")
            # Préremplit le formulaire (sauf mot de passe).
            return render_template(
                "register.html",
                form=request.form,
            )

        user = Utilisateur(
            nom=request.form["nom"].strip(),
            prenom=request.form["prenom"].strip(),
            email=email,
            campus=request.form["campus"].strip(),
        )
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()

        # Connexion automatique après inscription.
        session.clear()
        session["user_id"] = user.id
        flash("Compte créé. Bienvenue sur CampusGive.", "success")
        return redirect(url_for("annonces.liste"))

    return render_template("register.html", form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Connexion d'un utilisateur existant."""
    if "user_id" in session:
        return redirect(url_for("annonces.liste"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = Utilisateur.query.filter_by(email=email).first()
        # Vérification combinée pour éviter de divulguer si l'email existe.
        if user is None or not user.check_password(password):
            flash("Email ou mot de passe incorrect.", "error")
            return render_template("login.html", email=email)

        session.clear()
        session["user_id"] = user.id
        flash(f"Bienvenue {user.prenom}.", "success")
        return redirect(url_for("annonces.liste"))

    return render_template("login.html", email="")


@bp.route("/logout", methods=["POST"])
def logout():
    """Déconnexion. POST uniquement pour empêcher CSRF via lien."""
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("index"))
