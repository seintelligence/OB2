import streamlit as st
import os
from models import Projet, ModeleMur, InstanceMur, Document, TypeDocument, Ouverture, Statut

def sauvegarder_document(fichier, type_doc: TypeDocument) -> Document:
    """Sauvegarde un document uploadé dans le dossier documents"""
    if not os.path.exists("documents"):
        os.makedirs("documents")
    
    chemin = os.path.join("documents", fichier.name)
    with open(chemin, "wb") as f:
        f.write(fichier.getbuffer())
    
    return Document(fichier.name, type_doc, chemin)


