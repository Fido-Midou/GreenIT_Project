"""Tests d'intégration end-to-end du site CampusGive.

Utilise le test_client de Flask pour vérifier les flux principaux :
inscription, connexion, CRUD annonces, sécurité.
"""
from backend import create_app
from backend.models import db, Utilisateur, Annonce
import sqlite3
import os


def run_tests():
    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()
    failed = []
    passed = 0

    def check(label, cond, detail=""):
        nonlocal passed
        if cond:
            print(f"  ✓ {label}")
            passed += 1
        else:
            print(f"  ✗ {label}  {detail}")
            failed.append(label)

    # --- 1. Pages publiques ---
    print("\n[1] Pages publiques")
    r = client.get("/")
    check("Page d'accueil 200", r.status_code == 200)
    check("HTML accueil < 5 Ko", len(r.data) < 5000, f"({len(r.data)} octets)")
    check("Engagements écolo présents", b"engagements" in r.data.lower() or b"\xc3\xa9cologiques" in r.data)

    r = client.get("/annonces")
    check("Liste annonces 200", r.status_code == 200)
    check("Annonces de seed visibles", b"Manuel de math" in r.data)

    r = client.get("/inexistant")
    check("404 sur route inexistante", r.status_code == 404)

    # --- 2. Auth requise ---
    print("\n[2] Protection des routes")
    r = client.get("/profil")
    check("Profil sans auth → 302", r.status_code == 302)
    r = client.get("/admin/")
    check("Admin sans auth → 302", r.status_code == 302)
    r = client.get("/annonces/nouvelle")
    check("Création annonce sans auth → 302", r.status_code == 302)

    # --- 3. Inscription ---
    print("\n[3] Inscription")
    r = client.post(
        "/register",
        data={
            "nom": "Test",
            "prenom": "User",
            "email": "test@efrei.net",
            "campus": "Test",
            "password": "testpass123",
            "password_confirm": "testpass123",
        },
        follow_redirects=False,
    )
    check("POST /register → 302 (succès)", r.status_code == 302)
    with app.app_context():
        u = Utilisateur.query.filter_by(email="test@efrei.net").first()
        check("Utilisateur créé en BDD", u is not None)
        if u:
            check(
                "Mot de passe hashé (pas en clair)",
                u.mot_de_passe_hash != "testpass123" and len(u.mot_de_passe_hash) > 50,
            )
            check("Hash bcrypt valide", u.check_password("testpass123"))
            check("Hash bcrypt rejette mauvais mdp", not u.check_password("wrong"))

    # Validation : email vide (déconnexion d'abord, sinon redirect)
    with client.session_transaction() as sess:
        sess.clear()
    r = client.post(
        "/register",
        data={"nom": "X", "prenom": "X", "email": "", "campus": "X",
              "password": "abcdefgh", "password_confirm": "abcdefgh"},
    )
    check("Inscription avec email vide → erreur affichée", b"invalide" in r.data)

    # Validation : mots de passe différents
    with client.session_transaction() as sess:
        sess.clear()
    r = client.post(
        "/register",
        data={"nom": "X", "prenom": "X", "email": "x@y.fr", "campus": "X",
              "password": "abcdefgh", "password_confirm": "different"},
    )
    check("Inscription avec mdp non concordants → erreur", b"correspondent" in r.data)

    # --- 4. Connexion ---
    print("\n[4] Connexion")
    # Mauvais mdp
    r = client.post("/login", data={"email": "alice.dupont@efrei.net", "password": "wrong"})
    check("Login mauvais mdp → message d'erreur", b"incorrect" in r.data.lower())

    # Bon login
    with client.session_transaction() as sess:
        sess.clear()
    r = client.post(
        "/login",
        data={"email": "alice.dupont@efrei.net", "password": "alice12345"},
        follow_redirects=False,
    )
    check("Login alice → 302", r.status_code == 302)
    with client.session_transaction() as sess:
        check("user_id en session", "user_id" in sess)

    # --- 5. Création d'annonce (alice est connectée) ---
    print("\n[5] CRUD Annonces (utilisateur connecté)")
    r = client.post(
        "/annonces/nouvelle",
        data={
            "titre": "Test annonce intégration",
            "description": "Description de test pour l'intégration.",
            "categorie": "livres",
            "etat": "neuf",
            "type_annonce": "don",
        },
        follow_redirects=False,
    )
    check("Création annonce → 302", r.status_code == 302)
    with app.app_context():
        a = Annonce.query.filter_by(titre="Test annonce intégration").first()
        check("Annonce en BDD", a is not None)
        annonce_id = a.id if a else None

    # Lecture
    if annonce_id:
        r = client.get(f"/annonces/{annonce_id}")
        check("Détail annonce 200", r.status_code == 200)
        check("Titre dans la page détail", b"Test annonce int" in r.data)

        # Modification
        r = client.post(
            f"/annonces/{annonce_id}/modifier",
            data={
                "titre": "Test annonce modifiée",
                "description": "Mise à jour.",
                "categorie": "livres",
                "etat": "bon_etat",
                "type_annonce": "don",
                "statut": "disponible",
            },
            follow_redirects=False,
        )
        check("Modification annonce → 302", r.status_code == 302)

        # Suppression
        r = client.post(f"/annonces/{annonce_id}/supprimer", follow_redirects=False)
        check("Suppression annonce → 302", r.status_code == 302)
        with app.app_context():
            check("Annonce bien supprimée", Annonce.query.get(annonce_id) is None)

    # --- 6. Permissions : alice ne peut pas modifier l'annonce de bilal ---
    print("\n[6] Contrôle d'accès")
    with app.app_context():
        bilal = Utilisateur.query.filter_by(email="bilal.martin@efrei.net").first()
        annonce_bilal = Annonce.query.filter_by(id_utilisateur=bilal.id).first()
        bilal_id = annonce_bilal.id if annonce_bilal else None
    if bilal_id:
        r = client.post(
            f"/annonces/{bilal_id}/modifier",
            data={"titre": "PIRATÉ", "description": "x", "categorie": "livres",
                  "etat": "neuf", "type_annonce": "don"},
        )
        check("Alice ne peut PAS modifier annonce de Bilal → 403", r.status_code == 403)

    # --- 7. Tentative d'injection SQL ---
    print("\n[7] Sécurité SQL injection")
    with client.session_transaction() as sess:
        sess.clear()
    r = client.post(
        "/login",
        data={"email": "'; DROP TABLE utilisateurs; --", "password": "x"},
    )
    check("Login avec payload SQLi → 200 (page d'erreur)", r.status_code == 200)
    with app.app_context():
        # Si l'injection avait marché, la table n'existerait plus.
        nb = Utilisateur.query.count()
        check(f"Table utilisateurs intacte (count={nb})", nb >= 3)

    # --- 8. Admin ---
    print("\n[8] Panneau admin")
    with client.session_transaction() as sess:
        sess.clear()
    r = client.post("/login", data={"email": "admin@campusgive.fr", "password": "AdminCampus2026!"})
    check("Login admin → 302", r.status_code == 302)

    r = client.get("/admin/")
    check("Dashboard admin 200", r.status_code == 200)
    check("Statistiques affichées", b"Utilisateurs" in r.data)

    r = client.get("/admin/users")
    check("Liste users admin 200", r.status_code == 200)
    check("Tous les comptes visibles", b"alice.dupont" in r.data and b"bilal.martin" in r.data)

    # --- 9. Vérification mots de passe en BDD via SQL direct ---
    print("\n[9] Mots de passe stockés (vérif SQL directe)")
    db_path = os.path.join(os.path.dirname(__file__), "campusgive.db")
    if not os.path.exists(db_path):
        # Essayer le chemin relatif Flask (instance/)
        db_path = "instance/campusgive.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT email, mot_de_passe_hash FROM utilisateurs LIMIT 5")
        rows = cur.fetchall()
        for email, h in rows:
            assert "alice12345" not in h and "AdminCampus2026" not in h, f"FUITE: mdp clair dans {email}"
            assert h.startswith(("$2a$", "$2b$", "$2y$")), f"Hash bcrypt invalide pour {email}"
        check(f"Aucun mdp en clair, tous bcrypt ({len(rows)} comptes vérifiés)", True)
        conn.close()
    else:
        print("  (BDD non trouvée pour vérif SQL directe)")

    # --- Récap ---
    total = passed + len(failed)
    print(f"\n{'='*50}")
    print(f"Résultat : {passed}/{total} tests passés")
    if failed:
        print("Échecs :")
        for f in failed:
            print(f"  - {f}")
        return 1
    else:
        print("✓ Tous les tests passent.")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
