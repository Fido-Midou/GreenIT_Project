"""Point d'entrée de l'application CampusGive.

Lance le serveur Flask en mode développement.
En production, utiliser gunicorn : `gunicorn app:app`.
"""
from backend import create_app

app = create_app()

if __name__ == "__main__":
    # En développement uniquement. En production, utiliser gunicorn.
    app.run(host="0.0.0.0", port=5000)
