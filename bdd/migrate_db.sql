-- Table pour les semaines de production
CREATE TABLE IF NOT EXISTS semaines_production (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    capacite INTEGER DEFAULT 0,
    est_travaillee BOOLEAN DEFAULT TRUE,
    UNIQUE(annee, numero)
);

-- Table de liaison entre les instances de mur et les semaines de production
CREATE TABLE IF NOT EXISTS allocation_production (
    semaine_id INTEGER,
    instance_mur_id INTEGER,
    PRIMARY KEY (semaine_id, instance_mur_id),
    FOREIGN KEY (semaine_id) REFERENCES semaines_production(id),
    FOREIGN KEY (instance_mur_id) REFERENCES instances_mur(id)
);

-- Fonction pour initialiser les semaines sur 6 mois glissants
INSERT OR IGNORE INTO semaines_production (annee, numero, est_travaillee)
WITH RECURSIVE
  cnt(annee, semaine) AS (
    SELECT strftime('%Y', 'now'), strftime('%W', 'now')
    UNION ALL
    SELECT 
      CASE 
        WHEN semaine = 52 THEN annee + 1 
        ELSE annee 
      END,
      CASE 
        WHEN semaine = 52 THEN 1 
        ELSE semaine + 1 
      END
    FROM cnt
    WHERE semaine < 52 AND annee * 100 + semaine < (SELECT strftime('%Y', 'now') || (strftime('%W', 'now') + 26))
  )
SELECT annee, semaine, TRUE FROM cnt;
