#!/bin/bash
# Script de build pour Render
# Installe les dépendances et initialise la base de données

# Arrête à la première erreur
set -e

echo "Installation des dépendances..."
pip install -r requirements.txt

echo "Initialisation de la base de données..."
python seed.py

echo "Build terminé avec succès!"
