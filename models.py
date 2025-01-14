from datetime import datetime
from typing import List, Optional, Dict, Tuple
from enum import Enum
from Cout.estimation_cout import process_wall_costs

class Statut(str, Enum):
    EN_COURS = "En cours"
    VALIDE = "Validé"
    TERMINE = "Terminé"

class StatutMur(str, Enum):
    INITIALISE = "Initialisé"
    EN_CONCEPTION = "En conception"
    EN_FABRICATION = "En fabrication"
    FABRIQUE = "Fabriqué"
    INSTALLE = "Installé"

class StatutProjet(str, Enum):
    INITIALISE = "Initialisé"
    EN_CONCEPTION = "En conception"
    EN_FABRICATION = "En fabrication"
    EN_INSTALLATION = "En installation"
    TERMINE = "Terminé"
    ANNULE = "Abandonné"
    NON_RETENU = "Non retenu"

class TypeDocument(str, Enum):
    PLAN = "Plan"
    DEVIS = "Devis"
    PHOTO = "Photo"
    FORMAT_3D = "Format 3D"
    VALIDATION_QUALITE = "Validation Qualité"
    INSTRUCTIONS_FABRICATION = "Instructions de Fabrication"
    AUTRE = "Autre"

class Document:
    def __init__(self, nom: str, type_doc: TypeDocument, chemin: str, id: int = None):
        self.id = id
        self.nom = nom
        self.type = type_doc
        self.chemin = chemin
        self.date_creation = datetime.now()
        
    def sauvegarder(self, db, projet_id=None, modele_id=None, instance_id=None):
        """Sauvegarde le document dans la base de données
        
        Args:
            db: Instance de DatabaseManager
            projet_id: ID du projet associé (optionnel)
            modele_id: ID du modèle de mur associé (optionnel)
            instance_id: ID de l'instance de mur associée (optionnel)
        
        Returns:
            Document: Le document sauvegardé avec son ID mis à jour
        """
        return db.creer_document(self, projet_id, modele_id, instance_id)
        
    def modifier(self, db):
        """Met à jour le document dans la base de données"""
        return db.modifier_document(self)
        
    def supprimer(self, db):
        """Supprime le document de la base de données"""
        if self.id:
            db.supprimer_document(self.id)

class Ouverture:
    def __init__(self, type_ouverture: str, largeur: float, hauteur: float, position_x: float, position_y: float):
        self.type = type_ouverture
        self.largeur = largeur
        self.hauteur = hauteur
        self.position_x = position_x
        self.position_y = position_y

class TypeIsolant(str, Enum):
    PAILLE = "Paille"
    CHANVRE = "Chanvre"
    FIBRE_BOIS = "Fibre de bois"

class ModeleMur:
    def __init__(self, reference: str, longueur: float, hauteur: float, epaisseur: float, isolant: TypeIsolant = TypeIsolant.PAILLE, id: int = None):
        self.id = id
        self.reference = reference
        self.longueur = longueur
        self.hauteur = hauteur
        self.epaisseur = epaisseur
        self.cout = 0
        self.statut = Statut.EN_COURS
        self.isolant = isolant
        self.ouvertures: List[Ouverture] = []
        self.documents: List[Document] = []
        self.instances: List['InstanceMur'] = []
    def calculer_cout(self):
        hauteur_cm = int(self.hauteur)  # Conversion en cm
        largeur_cm = int(self.longueur)  # Conversion en cm
        
        print("Demarrage calcul cout")
        cout_m2, cout_mur = process_wall_costs(hauteur_cm, largeur_cm)
        if cout_m2 is not None:
            self.cout = cout_mur
            return cout_mur
        else:
            self.cout = 0  # Valeur par défaut si le calcul n'est pas disponible
            return 0

class InstanceMur:
    def __init__(self, numero: int, modele: ModeleMur, id: int = None):
        self.id = id
        self.numero = numero
        self.modele = modele
        self.statut = Statut.EN_COURS
        self.documents: List[Document] = []

class Projet:
    def __init__(self, nom: str, description: str, id: int = None):
        self.id = id
        self.nom = nom
        self.description = description
        self.adresse = ""
        self.adresse_postale = ""  # Added property
        self.code_postal = ""      # Added property
        self.ville = ""            # Added property
        self.cout_total = 0
        self.statut = StatutProjet.EN_CONCEPTION
        self.date_creation = datetime.now()
        self.modeles_mur: List[ModeleMur] = []
        self.instances_mur: List[InstanceMur] = []
        self.documents: List[Document] = []
        
    def sauvegarder(self, db):
        """Sauvegarde le projet dans la base de données"""
        return db.creer_projet(self)
        
    def modifier(self, db):
        """Met à jour le projet dans la base de données"""
        return db.modifier_projet(self)
        
    def supprimer(self, db):
        """Supprime le projet de la base de données"""
        if self.id:
            db.supprimer_projet(self.id)

class SemainePlanDeProduction:
    def __init__(self, numero: int, annee: int, id: int = None):
        self.id = id
        self.numero = numero
        self.annee = annee
        self.capacite: int = 0
        self.est_travaillee: bool = True
        self.instances_mur: List[InstanceMur] = []
    
    def sauvegarder(self, db):
        """Sauvegarde ou met à jour la semaine dans la base de données"""
        return db.sauvegarder_semaine_production(self)
    
    def modifier(self, db):
        """Met à jour la semaine dans la base de données"""
        return db.modifier_semaine_production(self)

    def supprimer(self, db):
        """Supprime la semaine de la base de données"""
        db.supprimer_semaine_production(self.id)

    def allouer_instance_mur(self, instance_mur: InstanceMur, db):
        """Alloue une instance de mur à cette semaine"""
        if not self.est_travaillee:
            raise ValueError("Impossible d'allouer un mur à une semaine non travaillée")
        
        print(f"Debug - Allocation du mur {instance_mur.numero} à la semaine {self.numero}")
        db.allouer_instance_mur(self.id, instance_mur.id)
        if instance_mur not in self.instances_mur:
            self.instances_mur.append(instance_mur)
            print(f"Debug - Instance ajoutée à la liste des instances de la semaine")

    def retirer_instance_mur(self, instance_mur: InstanceMur, db):
        """Retire une instance de mur de cette semaine"""
        print(f"Debug - Retrait du mur {instance_mur.numero} de la semaine {self.numero}")
        db.retirer_instance_mur(self.id, instance_mur.id)
        if instance_mur in self.instances_mur:
            self.instances_mur.remove(instance_mur)
            print(f"Debug - Instance retirée de la liste des instances de la semaine")

class PlanificationProduction:
    """Gestionnaire du plan de production global"""
    def __init__(self, db):
        self.db = db
        self.semaines: Dict[int, SemainePlanDeProduction] = {}
        self.db.initialiser_semaines_production()  # S'assure que les semaines sont initialisées
        self._charger_semaines()

    def _charger_semaines(self):
        """Charge toutes les semaines depuis la base de données"""
        semaines_data = self.db.charger_toutes_semaines_production()
        self.semaines = {s.id: s for s in semaines_data if s is not None}

    def obtenir_semaine(self, annee: int, numero: int) -> Optional[SemainePlanDeProduction]:
        """Retourne une semaine spécifique"""
        semaine = next(
            (s for s in self.semaines.values() 
             if s.annee == annee and s.numero == numero),
            None
        )
        return semaine
    
    @staticmethod
    def obtenir_semaine_actuelle():
        """Retourne le numéro de la semaine actuelle"""
        return datetime.now().isocalendar()[1]

    def obtenir_semaines(self, seulementTravaillees=False, debutSemaine=None, maxSemaines=26) -> List[SemainePlanDeProduction]:
        """Retourne les semaines de production"""
        if debutSemaine is None:
            debutSemaine = self.obtenir_semaine_actuelle()

        annee_courante = datetime.now().year
        
        # S'assurer que toutes les semaines sont créées de manière continue
        semaines_necessaires = []
        for i in range(debutSemaine, debutSemaine + maxSemaines):
            # Ajuster pour le changement d'année si nécessaire
            annee = annee_courante
            numero_semaine = i
            if numero_semaine > 52:
                annee = annee_courante + 1
                numero_semaine = numero_semaine - 52

            # Obtenir la semaine existante ou en créer une nouvelle
            semaine = self.obtenir_semaine(annee, numero_semaine)
            if not semaine:
                # Créer une nouvelle semaine si elle n'existe pas
                semaine = SemainePlanDeProduction(numero_semaine, annee)
                semaine = semaine.sauvegarder(self.db)
                self.semaines[semaine.id] = semaine

            # Ajouter la semaine si elle correspond aux critères
            if not seulementTravaillees or semaine.est_travaillee:
                semaines_necessaires.append(semaine)

        return semaines_necessaires

    def definir_capacite_semaine(self, annee: int, numero: int, capacite: int):
        """Définit la capacité de production d'une semaine"""
        print(f"definir_capacite_semaine: {annee} semaine{numero} capacite {capacite}")
        semaine = self.obtenir_semaine(annee, numero)
        if semaine:
            semaine.capacite = capacite
            semaine.modifier(self.db)
        else:
            raise ValueError(f"Semaine {numero} de l'année {annee} non trouvée")

    def definir_semaine_travaillee(self, annee: int, numero: int, est_travaillee: bool):
        """Définit si une semaine est travaillée ou non"""
        print(f"definir semaine travaillee: {annee} semaine{numero} est_travaillee {est_travaillee}")
        semaine = self.obtenir_semaine(annee, numero)
        if semaine:
            semaine.est_travaillee = est_travaillee
            semaine.modifier(self.db)
        else:
            raise ValueError(f"Semaine {numero} de l'année {annee} non trouvée")

    def get_production_data(self, projet: Projet) -> Tuple[str, List[int]]:
        """
        Génère les données de production pour un projet spécifique sur 12 semaines
        
        Args:
            projet: Le projet dont on veut obtenir le plan de production
                
        Returns:
            Tuple contenant:
                - Le nom du projet
                - Une liste de 12 valeurs représentant le nombre de murs prévus par semaine
        """
        # Obtenir uniquement les semaines travaillées, triées par date
        semaines_travaillees = self.obtenir_semaines(True, self.obtenir_semaine_actuelle(), 12)
        
        # Initialiser le tableau des murs prévus par semaine
        murs_par_semaine = [0] * 12
        
        # Créer un set des IDs des instances du projet pour une recherche plus efficace
        ids_instances_projet = {instance.id for instance in projet.instances_mur}
        
        # Pour chaque semaine, compter les instances de mur du projet
        for idx, semaine in enumerate(semaines_travaillees):
            if idx >= 12:  # S'assurer de ne pas dépasser 12 semaines
                break
                
            # Compter uniquement les instances appartenant au projet donné
            nb_murs = sum(
                1 for instance in semaine.instances_mur 
                if instance.id in ids_instances_projet
            )
            
            murs_par_semaine[idx] = nb_murs
            
        return projet.nom, murs_par_semaine

    def get_all_production_data(self) -> Tuple[List[str], List[List[int]]]:
        """
        Génère les données de production pour tous les projets en fabrication
        
        Returns:
            Tuple contenant:
                - Liste des noms de projets
                - Matrice [projet x semaine] avec le nombre de murs prévus
        """
        # Filtrer les projets en fabrication
        projets_en_fabrication = [p for p in self.db.charger_tous_projets() 
                                if p.statut == StatutProjet.EN_FABRICATION]
        
        project_list = []
        manuf_plan = []
        
        # Obtenir les données pour chaque projet
        for projet in projets_en_fabrication:
            nom_projet, production_data = self.get_production_data(projet)
            project_list.append(nom_projet)
            manuf_plan.append(production_data)  # Utiliser production_data au lieu de get_instances_par_semaine
        
        return project_list, manuf_plan
    
    def get_instances_par_semaine(self, projet_nom: str) -> Dict[int, List[InstanceMur]]:
        """
        Retourne un dictionnaire des instances de mur par semaine pour un projet donné
        """
        instances_par_semaine = {}
        
        # Récupérer tous les projets
        projets = self.db.charger_tous_projets()
        
        projet = next((p for p in projets if p.nom == projet_nom), None)
        
        if not projet:
            print("Debug - Projet non trouvé")
            return {}
            
        # Pour chaque semaine travaillée
        semaines = self.obtenir_semaines(True)
        
        for semaine in semaines:
            
            # Filtrer les instances qui appartiennent au projet
            instances = []
            for instance in semaine.instances_mur:
                projet_instance = next(
                    (p for p in projets if any(
                        inst.id == instance.id for inst in p.instances_mur
                    )),
                    None
                )
                if projet_instance and projet_instance.id == projet.id:
                    instances.append(instance)

            if instances:
                instances_par_semaine[semaine.numero] = instances
                
        return instances_par_semaine

    def reaffecter_instance(self, instance_id: int, nouvelle_semaine: int):
        """
        Déplace une instance de mur vers une nouvelle semaine
        
        Args:
            instance_id: ID de l'instance à déplacer
            nouvelle_semaine: Numéro de la nouvelle semaine
        """
        # Trouver la semaine actuelle
        instance = None
        ancienne_semaine = None
        
        for semaine in self.semaines.values():
            for inst in semaine.instances_mur:
                if inst.id == instance_id:
                    instance = inst
                    ancienne_semaine = semaine
                    break
            if instance:
                break
        
        if not instance:
            raise ValueError("Instance non trouvée")
            
        # Trouver la nouvelle semaine
        semaine_cible = next(
            (s for s in self.semaines.values() if s.numero == nouvelle_semaine),
            None
        )
        
        if not semaine_cible:
            raise ValueError("Semaine cible non trouvée")
            
        # Vérifier la capacité
        if len(semaine_cible.instances_mur) >= semaine_cible.capacite:
            raise ValueError("Capacité de la semaine cible dépassée")
        
        # Effectuer le déplacement
        ancienne_semaine.retirer_instance_mur(instance, self.db)
        semaine_cible.allouer_instance_mur(instance, self.db)