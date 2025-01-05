# migration_script.py

import sqlite3
from models import StatutProjet

def migrate_database(db_file="bdd/construction_projects.db"):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    try:
        # Vérifier si la colonne statut existe déjà
        cur.execute("PRAGMA table_info(projets)")
        columns = [col[1] for col in cur.fetchall()]
        
        if 'statut' not in columns:
            print("Ajout de la colonne statut à la table projets...")
            
            # Créer une table temporaire avec la nouvelle structure
            cur.execute('''
                CREATE TABLE projets_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    description TEXT,
                    adresse_postale TEXT,
                    code_postal TEXT,
                    ville TEXT,
                    cout_total REAL DEFAULT 0,
                    statut TEXT DEFAULT 'En conception' NOT NULL,
                    date_creation TEXT NOT NULL
                )
            ''')
            
            # Copier les données existantes avec le statut par défaut
            cur.execute('''
                INSERT INTO projets_new (id, nom, description, adresse_postale, 
                                       code_postal, ville, cout_total, statut, date_creation)
                SELECT id, nom, description, adresse_postale, code_postal, ville, 
                       cout_total, 'En conception', date_creation
                FROM projets
            ''')
            
            # Supprimer l'ancienne table et renommer la nouvelle
            cur.execute('DROP TABLE projets')
            cur.execute('ALTER TABLE projets_new RENAME TO projets')
            
            print("Migration terminée avec succès!")
        else:
            print("La colonne statut existe déjà dans la table projets")
            
        conn.commit()
        
    except Exception as e:
        print(f"Erreur lors de la migration : {str(e)}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
