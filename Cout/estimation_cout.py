import win32com.client
import pythoncom  # Ajout de cet import
import os
from typing import Tuple, Optional
import time
import locale

class ExcelInteraction:
    def __init__(self, file_path: str = "Cout/Modele Devis v1.xlsx"):
        self.file_path = os.path.abspath(file_path)
        self.excel = None
        self.workbook = None
        locale.setlocale(locale.LC_NUMERIC, 'C')

    def connect_to_excel(self) -> bool:
        try:
            pythoncom.CoInitialize()  # Initialisation COM
            print(f"Connection à Excel pour le fichier: {self.file_path}")
            self.excel = win32com.client.Dispatch("Excel.Application")
            self.excel.Visible = False
            self.excel.DisplayAlerts = False
            
            print("Ouverture du classeur...")
            self.workbook = self.excel.Workbooks.Open(self.file_path)
            
            print("\nNoms définis disponibles:")
            for name in self.workbook.Names:
                print(f"- {name.Name}")
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la connexion: {str(e)}")
            self.cleanup()
            return False

    def format_decimal(self, value: float) -> str:
        """Formate correctement les nombres décimaux."""
        return str(value).replace(',', '.')

    def update_inputs(self, hauteur_mur: float, largeur_mur: float) -> bool:
        try:
            print("\nMise à jour des inputs")
            
            # Conversion explicite en float et formatage
            hauteur = float(self.format_decimal(hauteur_mur))
            largeur = float(self.format_decimal(largeur_mur))
            
            print(f"Écriture de la hauteur (valeur exacte): {hauteur}")
            self.workbook.Names("Hauteur_mur_cm").RefersToRange.Value = hauteur
            
            print(f"Écriture de la largeur (valeur exacte): {largeur}")
            self.workbook.Names("Largeur_mur_cm").RefersToRange.Value = largeur
            
            # Vérification des valeurs écrites
            hauteur_ecrite = self.workbook.Names("Hauteur_mur_cm").RefersToRange.Value
            largeur_ecrite = self.workbook.Names("Largeur_mur_cm").RefersToRange.Value
            print(f"Valeurs effectivement écrites dans Excel :")
            print(f"- Hauteur : {hauteur_ecrite}")
            print(f"- Largeur : {largeur_ecrite}")
            
            # Force le recalcul
            print("Forçage du recalcul...")
            self.workbook.Application.Calculate()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour: {str(e)}")
            return False

    def get_outputs(self) -> Tuple[Optional[float], Optional[float]]:
        try:
            print("\nRécupération des outputs")
            
            cout_m2 = round(self.workbook.Names("Cout_€_m2").RefersToRange.Value,2)
            cout_mur = round(self.workbook.Names("Cout_€_mur").RefersToRange.Value,2)
            
            print(f"Valeurs trouvées (brutes):")
            print(f"Cout_€_m2: {cout_m2}")
            print(f"Cout_€_mur: {cout_mur}")
            
            if cout_m2 is None or cout_mur is None:
                raise ValueError("Valeurs non trouvées")
                
            return float(cout_m2), float(cout_mur)
            
        except Exception as e:
            print(f"Erreur lors de la récupération: {str(e)}")
            return None, None

    def cleanup(self):
        try:
            if hasattr(self, 'workbook') and self.workbook:
                self.workbook.Close(SaveChanges=False)
            if hasattr(self, 'excel') and self.excel:
                self.excel.Quit()
        except Exception as e:
            print(f"Erreur lors du nettoyage: {str(e)}")

def process_wall_costs(hauteur_mur_cm: float, largeur_mur_cm: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Traite les coûts du mur avec des dimensions en centimètres.
    Les valeurs peuvent être décimales (ex: 300.5).
    """
    print(f"\nTraitement pour un mur de {hauteur_mur_cm}cm x {largeur_mur_cm}cm")
    excel = ExcelInteraction()
    
    try:
        if not excel.connect_to_excel():
            raise ConnectionError("Impossible de se connecter à Excel")
        
        if not excel.update_inputs(hauteur_mur_cm, largeur_mur_cm):
            raise ValueError("Erreur lors de la mise à jour des entrées")
        
        cout_m2, cout_mur = excel.get_outputs()
        if cout_m2 is None or cout_mur is None:
            raise ValueError("Erreur lors de la récupération des sorties")
        
        print(f"Traitement terminé avec succès : {cout_m2}€/m² - {cout_mur}€ total")
        return cout_m2, cout_mur
        
    except Exception as e:
        print(f"Erreur lors du traitement: {str(e)}")
        return None, None
        
    finally:
        excel.cleanup()