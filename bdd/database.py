import sqlite3
from datetime import datetime
from models import (Projet, ModeleMur, InstanceMur, Document, TypeDocument, 
                   TypeIsolant, Ouverture, Statut, StatutProjet, SemainePlanDeProduction)

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
                date_creation TEXT NOT NULL,
                statut TEXT NOT NULL
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
                          
            CREATE TABLE IF NOT EXISTS semaines_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                annee INTEGER NOT NULL,
                numero INTEGER NOT NULL,
                capacite INTEGER DEFAULT 0,
                est_travaillee BOOLEAN DEFAULT TRUE,
                UNIQUE(annee, numero)
            );

            CREATE TABLE IF NOT EXISTS allocation_production (
                semaine_id INTEGER NOT NULL,
                instance_mur_id INTEGER NOT NULL,
                PRIMARY KEY (semaine_id, instance_mur_id),
                FOREIGN KEY (semaine_id) REFERENCES semaines_production (id),
                FOREIGN KEY (instance_mur_id) REFERENCES instances_mur (id)
            );
        ''')
        conn.commit()
        conn.close()

    # Méthodes pour Document
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

    # Méthodes pour ModeleMur
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

    # Méthodes pour InstanceMur
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

    # Méthodes pour Projet
    def charger_tous_projets(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projets")
        projets_data = cur.fetchall()
        
        projets = []
        for projet_data in projets_data:
            projet = self.charger_projet(projet_data['id'])
            projets.append(projet)
        
        conn.close()
        return projets

    def charger_projet(self, projet_id):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM projets WHERE id = ?", (projet_id,))
        projet_data = cur.fetchone()
        
        projet = Projet(projet_data['nom'], projet_data['description'], id=projet_id)
        projet.cout_total = projet_data['cout_total']
        projet.date_creation = datetime.fromisoformat(projet_data['date_creation'])
        projet.statut = StatutProjet(projet_data['statut']) if projet_data['statut'] else StatutProjet.EN_CONCEPTION
        projet.adresse_postale = projet_data['adresse_postale'] if projet_data['adresse_postale'] else ""
        projet.code_postal = projet_data['code_postal'] if projet_data['code_postal'] else ""
        projet.ville = projet_data['ville'] if projet_data['ville'] else ""
        
        # Charger documents du projet
        cur.execute("""
            SELECT * FROM documents 
            WHERE projet_id = ? AND modele_mur_id IS NULL AND instance_mur_id IS NULL
        """, (projet_id,))
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
            
            projet.modeles_mur.append(modele)
            
            # Charger instances du modèle
            cur.execute("""
                SELECT * FROM instances_mur 
                WHERE modele_mur_id = ? AND projet_id = ?
            """, (modele_id, projet_id))
            
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
        
        conn.close()
        return projet

    def creer_projet(self, projet):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO projets 
                (nom, description, adresse_postale, code_postal, ville, date_creation, cout_total, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (projet.nom, projet.description, projet.adresse_postale, projet.code_postal, 
                  projet.ville, projet.date_creation.isoformat(), projet.cout_total, projet.statut.value))
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
                    projet.statut.value,
                    projet.id
                ))
            conn.commit()
        finally:
            conn.close()

    def supprimer_projet(self, projet_id):
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # Supprimer tous les documents liés au projet
            cur.execute("DELETE FROM documents WHERE projet_id = ?", (projet_id,))
            # Supprimer toutes les instances de mur
            cur.execute("DELETE FROM instances_mur WHERE projet_id = ?", (projet_id,))
            # Supprimer tous les modèles de mur
            cur.execute("DELETE FROM modeles_mur WHERE projet_id = ?", (projet_id,))
            # Supprimer le projet lui-même
            cur.execute("DELETE FROM projets WHERE id = ?", (projet_id,))
            conn.commit()
        finally:
            conn.close()

    # Initialiser semaines production
    def initialiser_semaines_production(self):
        """Initialise les semaines de production pour les 6 prochains mois"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                WITH RECURSIVE dates(date) AS (
                    SELECT date('now', 'start of year')
                    UNION ALL
                    SELECT date(date, '+7 days')
                    FROM dates
                    WHERE date < date('now', '+6 months')
                )
                INSERT OR IGNORE INTO semaines_production (annee, numero, est_travaillee)
                SELECT 
                    cast(strftime('%Y', date) as integer),
                    cast(strftime('%W', date) as integer) + 1,
                    TRUE
                FROM dates;
            """)
            conn.commit()
        finally:
            conn.close()

    def charger_allocations_instances(self):
        """Charge toutes les allocations d'instances aux semaines"""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT instance_mur_id, numero
            FROM allocation_production
            JOIN semaines_production ON semaines_production.id = semaine_id
        """)
        allocations = {row[0]: row[1] for row in cur.fetchall()}
        cur.close()
        return allocations

    def charger_toutes_semaines_production(self):
        """Charge toutes les semaines de production avec leurs allocations"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sp.*, ap.instance_mur_id 
                FROM semaines_production sp
                LEFT JOIN allocation_production ap ON sp.id = ap.semaine_id
                ORDER BY sp.annee, sp.numero
            """)
            
            semaines_data = cur.fetchall()
            semaines = {}  # Utiliser un dictionnaire pour regrouper les instances par semaine
            
            for row in semaines_data:
                semaine_id = row['id']
                
                if semaine_id not in semaines:
                    # Créer la semaine si elle n'existe pas encore
                    semaine = SemainePlanDeProduction(
                        numero=row['numero'],
                        annee=row['annee'],
                        id=semaine_id
                    )
                    semaine.capacite = row['capacite']
                    semaine.est_travaillee = bool(row['est_travaillee'])
                    semaines[semaine_id] = semaine
                
                # Ajouter l'instance de mur si elle existe
                if row['instance_mur_id']:
                    instance = self._charger_instance_mur_specifique(row['instance_mur_id'])
                    if instance and instance not in semaines[semaine_id].instances_mur:
                        semaines[semaine_id].instances_mur.append(instance)
            
            return list(semaines.values())
        finally:
            conn.close()

    def sauvegarder_semaine_production(self, semaine):
        """Sauvegarde une nouvelle semaine de production"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO semaines_production (annee, numero, capacite, est_travaillee)
                VALUES (?, ?, ?, ?)
            """, (semaine.annee, semaine.numero, semaine.capacite, semaine.est_travaillee))
            semaine.id = cur.lastrowid
            conn.commit()
            return semaine
        finally:
            conn.close()

    def modifier_semaine_production(self, semaine):
        """Met à jour une semaine de production existante"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE semaines_production 
                SET capacite = ?, est_travaillee = ?
                WHERE id = ?
            """, (semaine.capacite, semaine.est_travaillee, semaine.id))
            conn.commit()
            return semaine
        finally:
            conn.close()

    def supprimer_semaine_production(self, semaine_id):
        """Supprime une semaine de production et ses allocations"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # Supprimer d'abord les allocations
            cur.execute("DELETE FROM allocation_production WHERE semaine_id = ?", (semaine_id,))
            # Puis supprimer la semaine
            cur.execute("DELETE FROM semaines_production WHERE id = ?", (semaine_id,))
            conn.commit()
        finally:
            conn.close()

    def allouer_instance_mur(self, semaine_id: int, instance_id: int):
        """Alloue une instance de mur à une semaine dans la base de données"""
        conn = self.get_connection()
        cur = conn.cursor()

        print(f"Debug - DB: Allocation instance {instance_id} à la semaine {semaine_id}")
        try:
            # D'abord supprimer toute allocation existante pour cette instance
            cur.execute("""
                DELETE FROM allocation_production 
                WHERE instance_mur_id = ?
            """, (instance_id,))
            
            # Puis insérer la nouvelle allocation
            cur.execute("""
                INSERT INTO allocation_production (semaine_id, instance_mur_id) 
                VALUES (?, ?)
            """, (semaine_id, instance_id))
            
            conn.commit()
            print("Debug - DB: Allocation sauvegardée avec succès")
        except Exception as e:
            print(f"Debug - DB: Erreur lors de l'allocation: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def retirer_instance_mur(self, semaine_id: int, instance_id: int):
        """Retire une instance de mur d'une semaine dans la base de données"""
        conn = self.get_connection()
        cur = conn.cursor()

        print(f"Debug - DB: Retrait instance {instance_id} de la semaine {semaine_id}")
        try:
            cur.execute("""
                DELETE FROM allocation_production 
                WHERE semaine_id = ? AND instance_mur_id = ?
            """, (semaine_id, instance_id))
            
            conn.commit()
            print("Debug - DB: Retrait effectué avec succès")
        except Exception as e:
            print(f"Debug - DB: Erreur lors du retrait: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _charger_instance_mur_specifique(self, instance_id):
        """Charge une instance de mur spécifique avec son modèle"""
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT i.*, m.* FROM instances_mur i
                JOIN modeles_mur m ON i.modele_mur_id = m.id
                WHERE i.id = ?
            """, (instance_id,))
            data = cur.fetchone()
            
            if not data:
                return None
                
            modele = ModeleMur(
                data['reference'],
                data['longueur'],
                data['hauteur'],
                data['epaisseur'],
                TypeIsolant(data['isolant']),
                id=data['modele_mur_id']
            )
            
            instance = InstanceMur(data['numero'], modele, id=instance_id)
            instance.statut = Statut(data['statut'])
            
            return instance
        finally:
            conn.close()    