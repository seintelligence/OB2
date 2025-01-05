import sqlite3
from datetime import datetime
from models import Projet, ModeleMur, InstanceMur, Document, TypeDocument, TypeIsolant, Ouverture, Statut, StatutProjet

class DatabaseManager:
    def __init__(self, db_file="bdd/construction_projects.db"):
        self.db_file = db_file
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn


    def init_database(self):
        conn = self.get_connection()
        cur = conn.cursor()

        cur.executescript('''
            CREATE TABLE IF NOT EXISTS projets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                description TEXT,
                adresse_postale TEXT,
                code_postal TEXT,
                ville TEXT,
                cout_total REAL DEFAULT 0,
                date_creation TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS modeles_mur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                projet_id INTEGER,
                reference TEXT NOT NULL,
                longueur INTEGER NOT NULL,
                hauteur INTEGER NOT NULL,
                epaisseur INTEGER NOT NULL,
                cout REAL DEFAULT 0,
                isolant TEXT DEFAULT 'Paille' NOT NULL,
                statut TEXT NOT NULL,
                FOREIGN KEY (projet_id) REFERENCES projets (id)
            );

            CREATE TABLE IF NOT EXISTS ouvertures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modele_mur_id INTEGER,
                type TEXT NOT NULL,
                largeur INTEGER NOT NULL,
                hauteur INTEGER NOT NULL,
                position_x INTEGER NOT NULL,
                position_y INTEGER NOT NULL,
                FOREIGN KEY (modele_mur_id) REFERENCES modeles_mur (id)
            );

            CREATE TABLE IF NOT EXISTS instances_mur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modele_mur_id INTEGER,
                projet_id INTEGER,
                numero INTEGER NOT NULL,
                statut TEXT NOT NULL,
                FOREIGN KEY (modele_mur_id) REFERENCES modeles_mur (id),
                FOREIGN KEY (projet_id) REFERENCES projets (id)
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                type TEXT NOT NULL,
                chemin TEXT NOT NULL,
                date_creation TEXT NOT NULL,
                projet_id INTEGER,
                modele_mur_id INTEGER,
                instance_mur_id INTEGER,
                FOREIGN KEY (projet_id) REFERENCES projets (id),
                FOREIGN KEY (modele_mur_id) REFERENCES modeles_mur (id),
                FOREIGN KEY (instance_mur_id) REFERENCES instances_mur (id)
            );
        ''')
        conn.commit()
        conn.close()

    # Documents
    def creer_document(self, document, projet_id=None, modele_id=None, instance_id=None):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO documents 
                (nom, type, chemin, date_creation, projet_id, modele_mur_id, instance_mur_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (document.nom, document.type.value, document.chemin, 
                document.date_creation.isoformat(), projet_id, modele_id, instance_id))
            document.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
        return document

    def modifier_document(self, document):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE documents 
                SET type = ?, chemin = ?
                WHERE id = ?
            """, (document.type.value, document.chemin, document.id))
            conn.commit()
        finally:
            conn.close()

    def supprimer_document(self, document_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM documents WHERE id = ?", (document_id,))
            conn.commit()
        finally:
            conn.close()

    # Modèles de mur
    def creer_modele_mur(self, modele, projet_id):
        # Calculer le coût avant la création
        modele.calculer_cout()
        
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO modeles_mur 
                (projet_id, reference, longueur, hauteur, epaisseur, cout, statut, isolant)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (projet_id, modele.reference, modele.longueur, modele.hauteur,
                modele.epaisseur, modele.cout, modele.statut.value, modele.isolant))
            modele.id = cur.lastrowid
            
            for ouverture in modele.ouvertures:
                cur.execute("""
                    INSERT INTO ouvertures 
                    (modele_mur_id, type, largeur, hauteur, position_x, position_y)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (modele.id, ouverture.type, ouverture.largeur, ouverture.hauteur,
                    ouverture.position_x, ouverture.position_y))
            
            conn.commit()
        finally:
            conn.close()
        return modele

    def modifier_modele_mur(self, modele):
        # Calculer le coût avant la modification
        modele.calculer_cout()
        
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE modeles_mur 
                SET reference = ?, longueur = ?, hauteur = ?, epaisseur = ?, 
                    cout = ?, statut = ?, isolant = ?
                WHERE id = ?
            """, (modele.reference, modele.longueur, modele.hauteur, 
                modele.epaisseur, modele.cout, modele.statut.value, modele.isolant, modele.id))
            
            cur.execute("DELETE FROM ouvertures WHERE modele_mur_id = ?", (modele.id,))
            for ouverture in modele.ouvertures:
                cur.execute("""
                    INSERT INTO ouvertures 
                    (modele_mur_id, type, largeur, hauteur, position_x, position_y)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (modele.id, ouverture.type, ouverture.largeur, ouverture.hauteur,
                    ouverture.position_x, ouverture.position_y))
            
            conn.commit()
        finally:
            conn.close()

    def supprimer_modele_mur(self, modele_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM documents WHERE modele_mur_id = ?", (modele_id,))
            cur.execute("DELETE FROM ouvertures WHERE modele_mur_id = ?", (modele_id,))
            cur.execute("DELETE FROM instances_mur WHERE modele_mur_id = ?", (modele_id,))
            cur.execute("DELETE FROM modeles_mur WHERE id = ?", (modele_id,))
            conn.commit()
        finally:
            conn.close()

    # Instances de mur
    def creer_instance_mur(self, instance, projet_id, modele_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO instances_mur 
                (modele_mur_id, projet_id, numero, statut)
                VALUES (?, ?, ?, ?)
            """, (modele_id, projet_id, instance.numero, instance.statut.value))
            instance.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
        return instance

    def modifier_instance_mur(self, instance):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE instances_mur 
                SET statut = ?
                WHERE id = ?
            """, (instance.statut.value, instance.id))
            conn.commit()
        finally:
            conn.close()

    def supprimer_instance_mur(self, instance_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM documents WHERE instance_mur_id = ?", (instance_id,))
            cur.execute("DELETE FROM instances_mur WHERE id = ?", (instance_id,))
            conn.commit()
        finally:
            conn.close()

    # Projets
    def charger_projets(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projets")
        projets_data = cur.fetchall()
        
        projets = []
        for projet_data in projets_data:
            projet_id = projet_data['id']
            projet = Projet(projet_data['nom'], projet_data['description'], id=projet_id)
            projet.cout_total = projet_data['cout_total']
            projet.adresse_postale = projet_data['adresse_postale'] if projet_data['adresse_postale'] else ""
            projet.code_postal = projet_data['code_postal'] if projet_data['code_postal'] else ""
            projet.ville = projet_data['ville'] if projet_data['ville'] else ""
            projet.date_creation = datetime.fromisoformat(projet_data['date_creation'])
            projet.statut = StatutProjet(projet_data['statut']) if projet_data['statut'] else StatutProjet.EN_CONCEPTION
            
            # Documents du projet
            cur.execute("""
                SELECT * FROM documents 
                WHERE projet_id = ? AND modele_mur_id IS NULL AND instance_mur_id IS NULL
            """, (projet_id,))
            for doc_data in cur.fetchall():
                doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
                doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
                projet.documents.append(doc)
            
            # Modèles de mur
            cur.execute("SELECT * FROM modeles_mur WHERE projet_id = ?", (projet_id,))
            for modele_data in cur.fetchall():
                modele_id = modele_data['id']
                modele = ModeleMur(
                    modele_data['reference'],
                    modele_data['longueur'],
                    modele_data['hauteur'],
                    modele_data['epaisseur'],
                    isolant=TypeIsolant(modele_data['isolant']),
                    id=modele_id
                )
                modele.cout = modele_data['cout']
                modele.statut = Statut(modele_data['statut'])
                
                # Ouvertures du modèle
                cur.execute("SELECT * FROM ouvertures WHERE modele_mur_id = ?", (modele_id,))
                for ouv_data in cur.fetchall():
                    ouverture = Ouverture(
                        ouv_data['type'],
                        ouv_data['largeur'],
                        ouv_data['hauteur'],
                        ouv_data['position_x'],
                        ouv_data['position_y']
                    )
                    modele.ouvertures.append(ouverture)
                
                # Documents du modèle
                cur.execute("SELECT * FROM documents WHERE modele_mur_id = ?", (modele_id,))
                for doc_data in cur.fetchall():
                    doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
                    doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
                    modele.documents.append(doc)
                
                projet.modeles_mur.append(modele)
                
                # Instances du modèle
                cur.execute("""
                    SELECT * FROM instances_mur 
                    WHERE modele_mur_id = ? AND projet_id = ?
                """, (modele_id, projet_id))
                
                for inst_data in cur.fetchall():
                    instance = InstanceMur(inst_data['numero'], modele, id=inst_data['id'])
                    instance.statut = Statut(inst_data['statut'])
                    
                    # Documents de l'instance
                    cur.execute("SELECT * FROM documents WHERE instance_mur_id = ?", (inst_data['id'],))
                    for doc_data in cur.fetchall():
                        doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
                        doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
                        instance.documents.append(doc)
                    
                    modele.instances.append(instance)
                    projet.instances_mur.append(instance)
            
            projets.append(projet)
        
        conn.close()
        return projets

    def creer_projet(self, projet):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO projets (nom, description, adresse_postale, code_postal, ville, date_creation, cout_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (projet.nom, projet.description, projet.adresse_postale, projet.code_postal, projet.ville,
                  projet.date_creation.isoformat(), projet.cout_total))
            projet.id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
        return projet

    def modifier_projet(self, projet):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE projets
                SET nom = ?,
                    description = ?,
                    cout_total = ?,
                    date_creation = ?, 
                    adresse_postale = ?,
                    code_postal = ?,
                    ville = ?,
                    statut = ?
                WHERE id = ?
            """, (
                    projet.nom,
                    projet.description,
                    projet.cout_total,
                    projet.date_creation.isoformat(),
                    projet.adresse_postale,
                    projet.code_postal,
                    projet.ville, 
                    projet.statut.value,  # Ajout du statut ici
                    projet.id
                ))
            conn.commit()
        finally:
            conn.close()

    def charger_projet_complet(self, projet_id):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
        projet_data = cur.fetchone()
        
        projet = Projet(projet_data['nom'], projet_data['description'], id=projet_id)
        projet.cout_total = projet_data['cout_total']
        projet.date_creation = datetime.fromisoformat(projet_data['date_creation'])
        projet.statut = StatutProjet(projet_data['statut'])
        
        # Charger documents du projet
        cur.execute("SELECT * FROM documents WHERE projet_id = ? AND modele_mur_id IS NULL AND instance_mur_id IS NULL", (projet_id,))
        for doc_data in cur.fetchall():
            doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
            doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
            projet.documents.append(doc)
        
        # Charger modèles de mur
        cur.execute("SELECT * FROM modeles_mur WHERE projet_id = ?", (projet_id,))
        for modele_data in cur.fetchall():
            modele_id = modele_data['id']
            modele = ModeleMur(
                modele_data['reference'], 
                modele_data['longueur'],
                modele_data['hauteur'],
                modele_data['epaisseur'],
                isolant=TypeIsolant(modele_data['isolant']),
                id=modele_id
            )
            modele.cout = modele_data['cout']
            modele.statut = Statut(modele_data['statut'])
            
            # Charger ouvertures du modèle
            cur.execute("SELECT * FROM ouvertures WHERE modele_mur_id = ?", (modele_id,))
            for ouv_data in cur.fetchall():
                ouverture = Ouverture(
                    ouv_data['type'],
                    ouv_data['largeur'],
                    ouv_data['hauteur'],
                    ouv_data['position_x'],
                    ouv_data['position_y']
                )
                modele.ouvertures.append(ouverture)
            
            # Charger documents du modèle
            cur.execute("SELECT * FROM documents WHERE modele_mur_id = ?", (modele_id,))
            for doc_data in cur.fetchall():
                doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
                doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
                modele.documents.append(doc)
                
            # Charger instances du modèle
            cur.execute("SELECT * FROM instances_mur WHERE modele_mur_id = ? AND projet_id = ?", (modele_id, projet_id))
            for inst_data in cur.fetchall():
                instance = InstanceMur(inst_data['numero'], modele, id=inst_data['id'])
                instance.statut = Statut(inst_data['statut'])
                
                # Charger documents de l'instance
                cur.execute("SELECT * FROM documents WHERE instance_mur_id = ?", (inst_data['id'],))
                for doc_data in cur.fetchall():
                    doc = Document(doc_data['nom'], TypeDocument(doc_data['type']), doc_data['chemin'], id=doc_data['id'])
                    doc.date_creation = datetime.fromisoformat(doc_data['date_creation'])
                    instance.documents.append(doc)
                
                modele.instances.append(instance)
                projet.instances_mur.append(instance)
                
            projet.modeles_mur.append(modele)
        
        conn.close()
        return projet
    
    def supprimer_projet(self, projet_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM documents WHERE projet_id = ?", (projet_id,))
            cur.execute("DELETE FROM instances_mur WHERE projet_id = ?", (projet_id,))
            cur.execute("DELETE FROM modeles_mur WHERE projet_id = ?", (projet_id,))
            cur.execute("DELETE FROM projets WHERE id = ?", (projet_id,))
            conn.commit()
        finally:
            conn.close()