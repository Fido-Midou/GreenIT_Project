"""Décorateurs pour protéger les routes nécessitant authentification ou droits admin."""
from functools import wraps
from flask import session, redirect, url_for, flash, abort
from .models import Utilisateur


def login_required(view):
    """Redirige vers /login si l'utilisateur n'est pas connecté."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Vous devez être connecté pour accéder à cette page.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Restreint l'accès aux utilisateurs avec role=admin."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Vous devez être connecté.", "error")
            return redirect(url_for("auth.login"))
        user = Utilisateur.query.get(session["user_id"])
        if user is None or not user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def get_current_user():
    """Retourne l'utilisateur courant (ou None)."""
    if "user_id" not in session:
        return None
    return Utilisateur.query.get(session["user_id"])
