-- Schéma de la base de données CampusGive.
-- En pratique, SQLAlchemy crée ces tables automatiquement via init_db().
-- Ce fichier sert de référence et permet une initialisation manuelle si besoin
-- (PostgreSQL prod). Compatible SQLite et PostgreSQL avec quelques ajustements.

-- =====================================================================
-- Table : utilisateurs
-- =====================================================================
CREATE TABLE IF NOT EXISTS utilisateurs (
    id                 INTEGER PRIMARY KEY,
    nom                VARCHAR(80)  NOT NULL,
    prenom             VARCHAR(80)  NOT NULL,
    email              VARCHAR(120) NOT NULL UNIQUE,
    mot_de_passe_hash  VARCHAR(255) NOT NULL,
    campus             VARCHAR(80)  NOT NULL,
    date_inscription   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role               VARCHAR(10)  NOT NULL DEFAULT 'user'
);

CREATE INDEX IF NOT EXISTS idx_utilisateurs_email
    ON utilisateurs(email);

-- =====================================================================
-- Table : annonces
-- =====================================================================
CREATE TABLE IF NOT EXISTS annonces (
    id                 INTEGER PRIMARY KEY,
    titre              VARCHAR(120) NOT NULL,
    description        TEXT         NOT NULL,
    categorie          VARCHAR(50)  NOT NULL,
    etat               VARCHAR(20)  NOT NULL,
    type_annonce       VARCHAR(10)  NOT NULL,
    statut             VARCHAR(20)  NOT NULL DEFAULT 'disponible',
    date_publication   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_utilisateur     INTEGER      NOT NULL,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id) ON DELETE CASCADE
);

-- Index sur les colonnes fréquemment filtrées (consigne 4.2.c).
CREATE INDEX IF NOT EXISTS idx_annonces_categorie     ON annonces(categorie);
CREATE INDEX IF NOT EXISTS idx_annonces_statut        ON annonces(statut);
CREATE INDEX IF NOT EXISTS idx_annonces_date_pub      ON annonces(date_publication);
CREATE INDEX IF NOT EXISTS idx_annonces_utilisateur   ON annonces(id_utilisateur);
