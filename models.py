"""Modèles de données : Utilisateur et Annonce.

Conforme à la conception de la Partie 1 (cf. diagramme de classes).
Index ajoutés sur les colonnes fréquemment interrogées (consigne 4.2.c).
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()


def _utcnow():
    """Helper : datetime UTC, conforme aux bonnes pratiques."""
    return datetime.now(timezone.utc)


class Utilisateur(db.Model):
    """Compte utilisateur de la plateforme."""

    __tablename__ = "utilisateurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    # index=True : recherches fréquentes par email (login).
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # Stocke le hash bcrypt en bytes encodés UTF-8 (60 caractères).
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    campus = db.Column(db.String(80), nullable=False)
    date_inscription = db.Column(db.DateTime, default=_utcnow, nullable=False)
    role = db.Column(db.String(10), default="user", nullable=False)  # user | admin

    # Relation 1-N : un utilisateur publie plusieurs annonces.
    # cascade="all, delete-orphan" : supprimer un user supprime ses annonces.
    annonces = db.relationship(
        "Annonce",
        backref="auteur",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        """Hashe le mot de passe avec bcrypt (cost factor 12, recommandé OWASP)."""
        salt = bcrypt.gensalt(rounds=12)
        self.mot_de_passe_hash = bcrypt.hashpw(
            password.encode("utf-8"), salt
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Vérifie un mot de passe contre le hash stocké."""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.mot_de_passe_hash.encode("utf-8"),
        )

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"<Utilisateur {self.email}>"


class Annonce(db.Model):
    """Annonce de don ou d'échange déposée par un utilisateur."""

    __tablename__ = "annonces"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # index=True : filtre fréquent par catégorie.
    categorie = db.Column(db.String(50), nullable=False, index=True)
    etat = db.Column(db.String(20), nullable=False)  # neuf | bon_etat | usage
    type_annonce = db.Column(db.String(10), nullable=False)  # don | echange
    statut = db.Column(
        db.String(20), default="disponible", nullable=False, index=True
    )  # disponible | reserve | donne
    date_publication = db.Column(
        db.DateTime, default=_utcnow, nullable=False, index=True
    )
    id_utilisateur = db.Column(
        db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Annonce {self.id} - {self.titre}>"


# Catégories autorisées (validation côté serveur).
CATEGORIES = [
    "livres",
    "informatique",
    "vetements",
    "mobilier",
    "fournitures",
    "electromenager",
    "autre",
]
ETATS = ["neuf", "bon_etat", "usage"]
TYPES = ["don", "echange"]
STATUTS = ["disponible", "reserve", "donne"]


def init_db(app):
    """Initialise SQLAlchemy avec l'app et crée les tables si absentes."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
