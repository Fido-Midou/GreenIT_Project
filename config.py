"""Configuration de l'application Flask.

Sépare les paramètres par environnement (dev / prod) et lit les variables
sensibles depuis le fichier .env (jamais versionné).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration de base, partagée par tous les environnements."""

    # Clé secrète pour signer les sessions Flask. Lue depuis .env.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-CHANGE-IN-PRODUCTION")

    # Base de données. SQLite par défaut (sobre, pas de serveur),
    # PostgreSQL en prod si DATABASE_URL est fourni.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///campusgive.db"
    )
    # Heroku/Render fournissent parfois "postgres://" → SQLAlchemy attend "postgresql://"
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    # Désactive le tracking des modifications (gain mémoire, recommandé).
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cookies de session : sécurité minimale.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # En production, mettre à True (HTTPS obligatoire).
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    # Pagination par défaut (consigne : max 20 résultats par page).
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


def get_config():
    """Retourne la classe de config selon FLASK_ENV."""
    return (
        ProductionConfig
        if os.environ.get("FLASK_ENV") == "production"
        else DevelopmentConfig
    )
