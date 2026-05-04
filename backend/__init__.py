"""Factory de l'application Flask CampusGive.

Pattern factory recommandé pour Flask : permet plusieurs instances (tests, prod)
et évite les imports circulaires.
"""
from flask import Flask, render_template, redirect, url_for
from .models import db, init_db
from .decorators import get_current_user
from config import get_config


def create_app():
    """Crée et configure l'application Flask."""
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )
    app.config.from_object(get_config())

    # Initialise la base de données.
    init_db(app)

    # Rend l'utilisateur courant disponible dans tous les templates.
    @app.context_processor
    def inject_user():
        return {"current_user": get_current_user()}

    # Page d'accueil.
    @app.route("/")
    def index():
        return render_template("index.html")

    # Enregistre les blueprints.
    from .auth import bp as auth_bp
    from .annonces import bp as annonces_bp, bp_user as user_bp
    from .admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(annonces_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Gestion des erreurs avec codes HTTP appropriés.
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app
