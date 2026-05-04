"""Script d'initialisation : crée un compte admin et quelques annonces de démo.

Usage : python seed.py

automatiquement lancé par build.sh (cas utilisation render.com)
"""
from backend import create_app
from backend.models import db, Utilisateur, Annonce


SAMPLE_USERS = [
    {
        "nom": "Admin",
        "prenom": "Super",
        "email": "admin@campusgive.fr",
        "campus": "EFREI Villejuif",
        "role": "admin",
        "password": "AdminCampus2026!",
    },
    {
        "nom": "Dupont",
        "prenom": "Alice",
        "email": "alice.dupont@efrei.net",
        "campus": "EFREI Villejuif",
        "role": "user",
        "password": "alice12345",
    },
    {
        "nom": "Martin",
        "prenom": "Bilal",
        "email": "bilal.martin@efrei.net",
        "campus": "EFREI Villejuif",
        "role": "user",
        "password": "bilal12345",
    },
]

SAMPLE_ANNONCES = [
    {
        "auteur_email": "alice.dupont@efrei.net",
        "titre": "Manuel de mathématiques pour ingénieur",
        "description": "Manuel de maths utilisé en première année, en bon état, quelques annotations au crayon. Cherche à le donner à un étudiant qui rentre en prépa intégrée.",
        "categorie": "livres",
        "etat": "bon_etat",
        "type_annonce": "don",
    },
    {
        "auteur_email": "alice.dupont@efrei.net",
        "titre": "Lampe de bureau LED",
        "description": "Lampe de bureau LED orientable, marche parfaitement. Je m'en sépare car je déménage. À récupérer sur le campus.",
        "categorie": "mobilier",
        "etat": "bon_etat",
        "type_annonce": "don",
    },
    {
        "auteur_email": "bilal.martin@efrei.net",
        "titre": "Souris filaire contre clavier mécanique",
        "description": "J'échange une souris filaire neuve (jamais utilisée, encore dans la boîte) contre un clavier mécanique d'occasion. Préférence pour switches rouges ou bruns.",
        "categorie": "informatique",
        "etat": "neuf",
        "type_annonce": "echange",
    },
    {
        "auteur_email": "bilal.martin@efrei.net",
        "titre": "Pull en laine taille M",
        "description": "Pull en laine couleur bleu marine, taille M. Acheté l'an dernier, peu porté. Donné car il ne me va plus.",
        "categorie": "vetements",
        "etat": "bon_etat",
        "type_annonce": "don",
    },
    {
        "auteur_email": "alice.dupont@efrei.net",
        "titre": "Bouilloire électrique 1,7 L",
        "description": "Bouilloire en très bon état, fonctionne parfaitement. Donnée car j'ai reçu la même en cadeau.",
        "categorie": "electromenager",
        "etat": "bon_etat",
        "type_annonce": "don",
    },
]


def run():
    app = create_app()
    with app.app_context():
        # Reset (en dev uniquement) : décommenter si besoin de repartir de zéro.
        # db.drop_all()
        # db.create_all()

        # Vérification : si l'admin existe déjà, abandon du seed
        admin_exists = Utilisateur.query.filter_by(email="admin@campusgive.fr").first()
        if admin_exists:
            print("Les données de seed existent déjà, abandon.")
            print("  (Compte admin déjà présent)")
            return

        # Crée les utilisateurs s'ils n'existent pas.
        users_by_email = {}
        for data in SAMPLE_USERS:
            user = Utilisateur.query.filter_by(email=data["email"]).first()
            if user is None:
                user = Utilisateur(
                    nom=data["nom"],
                    prenom=data["prenom"],
                    email=data["email"],
                    campus=data["campus"],
                    role=data["role"],
                )
                user.set_password(data["password"])
                db.session.add(user)
                print(f"+ Utilisateur créé : {data['email']}")
            users_by_email[data["email"]] = user

        db.session.commit()

        # Crée les annonces si elles n'existent pas (déduplique sur le titre).
        for data in SAMPLE_ANNONCES:
            existing = Annonce.query.filter_by(titre=data["titre"]).first()
            if existing:
                continue
            auteur = users_by_email[data["auteur_email"]]
            annonce = Annonce(
                titre=data["titre"],
                description=data["description"],
                categorie=data["categorie"],
                etat=data["etat"],
                type_annonce=data["type_annonce"],
                id_utilisateur=auteur.id,
            )
            db.session.add(annonce)
            print(f"+ Annonce créée : {data['titre']}")

        db.session.commit()
        print("\nSeed terminé.")
        print("  Compte admin   : admin@campusgive.fr / AdminCampus2026!")
        print("  Compte démo 1  : alice.dupont@efrei.net / alice12345")
        print("  Compte démo 2  : bilal.martin@efrei.net / bilal12345")


if __name__ == "__main__":
    run()
