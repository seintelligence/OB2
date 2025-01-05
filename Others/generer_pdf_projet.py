from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
import streamlit as st
from models import StatutProjet

def generer_pdf_projet(projet):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph(f"Projet: {projet.nom}", title_style))
    
    # Informations générales
    story.append(Paragraph("Informations générales", styles['Heading2']))
    story.append(Paragraph(f"État: {projet.statut.value}", styles['Normal']))
    story.append(Paragraph(f"Date de création: {projet.date_creation.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Paragraph(f"Adresse: {projet.adresse if projet.adresse else 'Non spécifiée'}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Documents
    story.append(Paragraph("Documents", styles['Heading2']))
    if projet.documents:
        for doc in projet.documents:
            story.append(Paragraph(f"• {doc.nom} ({doc.type.value})", styles['Normal']))
    else:
        story.append(Paragraph("Aucun document", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Coût
    story.append(Paragraph("Coût", styles['Heading2']))
    cout_total = sum(round(modele.cout * len(modele.instances), 2) for modele in projet.modeles_mur) if projet.modeles_mur else 0
    story.append(Paragraph(f"Coût total estimé: {cout_total}€", styles['Normal']))
    
    if projet.modeles_mur:
        story.append(Paragraph("Détail des coûts:", styles['Normal']))
        for modele in projet.modeles_mur:
            cout_modele = modele.cout * len(modele.instances)
            story.append(Paragraph(
                f"• Modèle {modele.reference}: {modele.cout}€ × {len(modele.instances)} instances = {cout_modele}€",
                styles['Normal']
            ))
    story.append(Spacer(1, 20))
    
    # Murs
    story.append(Paragraph("Murs", styles['Heading2']))
    if projet.statut == StatutProjet.EN_CONCEPTION:
        if projet.modeles_mur:
            for modele in projet.modeles_mur:
                story.append(Paragraph(f"Modèle {modele.reference}", styles['Heading3']))
                story.append(Paragraph(
                    f"Dimensions: {modele.longueur}×{modele.hauteur}×{modele.epaisseur}cm",
                    styles['Normal']
                ))
                story.append(Paragraph(f"Coût unitaire: {modele.cout}€", styles['Normal']))
                story.append(Paragraph(f"Nombre d'instances: {len(modele.instances)}", styles['Normal']))
                
                if modele.ouvertures:
                    story.append(Paragraph("Ouvertures:", styles['Normal']))
                    for ouv in modele.ouvertures:
                        story.append(Paragraph(
                            f"• {ouv.type}: {ouv.largeur}×{ouv.hauteur}cm @ ({ouv.position_x}, {ouv.position_y})",
                            styles['Normal']
                        ))
                story.append(Spacer(1, 10))
    else:
        instances_filtrees = [inst for inst in projet.instances_mur 
                            if inst.modele.statut != StatutProjet.EN_CONCEPTION]
        if instances_filtrees:
            for instance in sorted(instances_filtrees, key=lambda x: x.numero):
                story.append(Paragraph(
                    f"Instance n°{instance.numero} - {instance.modele.reference}",
                    styles['Heading3']
                ))
                story.append(Paragraph(f"Statut: {instance.statut.value}", styles['Normal']))
                story.append(Paragraph(
                    f"Dimensions: {instance.modele.longueur}×{instance.modele.hauteur}×{instance.modele.epaisseur}cm",
                    styles['Normal']
                ))
                
                if instance.documents:
                    story.append(Paragraph("Documents associés:", styles['Normal']))
                    for doc in instance.documents:
                        story.append(Paragraph(f"• {doc.nom} ({doc.type.value})", styles['Normal']))
                story.append(Spacer(1, 10))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf