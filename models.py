from datetime import datetime
from typing import List
from enum import Enum
from Cout.estimation_cout import process_wall_costs

class Statut(str, Enum):
    EN_COURS = "En cours"
    VALIDE = "Validé"
    TERMINE = "Terminé"

class StatutProjet(str, Enum):
    INITIALISE = "Initialisé"
    EN_CONCEPTION = "En conception"
    EN_FABRICATION = "En fabrication"
    EN_INSTALLATION = "En installation"
    TERMINE = "Terminé"

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
        self.adresse = ""  # Nouvelle propriété
        self.cout_total = 0
        self.statut = StatutProjet.EN_CONCEPTION
        self.date_creation = datetime.now()
        self.modeles_mur: List[ModeleMur] = []
        self.instances_mur: List[InstanceMur] = []
        self.documents: List[Document] = []