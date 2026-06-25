import csv
import json
import os
from pypdf import PdfReader
import ollama
from pydantic import BaseModel, Field
from typing import Literal

# --- 1. CONFIGURATION DE LA HIÉRARCHIE ---
HIERARCHIE = {
    "CircuitProtection": ["ESD_TVS", "fuseHolders", "fuses"],
    "Connector": ["Dupont", "JST", "pinHeader_pinSocket", "powerJacks"],
    "Electromechanical": ["motors", "relays", "audio", "quartz"],
    "EmbeddedSolutions": ["computing", "developmentKits", "embeddedProcessors", "sensorModules"],
    "PassiveComponents": ["capacitors", "inductors", "potentiometers", "resistors", "signalTransformers"],
    "Power": ["AC-DC_Converters", "DC-DC_Converters", "powerManagementICs"],
    "Semiconductors": [
        "amplifier", "buffer", "communicationRF", "diodes", "gateDriver",
        "gpioExpander", "integratedCircuits", "memoryICs", "motorDriver",
        "transceiverEth", "transceiverRF", "transistors", "wireless_RFSemiconductors"
    ],
    "Sensors": ["current", "encoders", "IMU", "magnetic", "pressure", "proximity", "temperature"],
    "ThermalManagement": ["fans", "heatSinks"],
    "Tools": ["soldering"],
    "WireCables": ["cableAssemblies", "multiConductorCables"],
    "Optoelectronic": ["IR", "LED", "ledDriver", "phototransistor"]
}

ToutesCategories = tuple(HIERARCHIE.keys())
ToutesSousCategories = tuple([item for sublist in HIERARCHIE.values() for item in sublist])

class ClassificationDatasheet(BaseModel):
    justification: str = Field(description="Explication très brève de la fonction du composant.")
    categorie: Literal[ToutesCategories] = Field(description="La catégorie principale choisie.")
    sous_categorie: Literal[ToutesSousCategories] = Field(description="La sous-catégorie associée.")

# --- 2. FONCTION DE CLASSIFICATION ---
def classer_composant(texte_source):
    arbre_formatte = json.dumps(HIERARCHIE, indent=2)
    prompt = f"""
    Voici les informations/texte d'un composant électronique :
    {texte_source}
    
    Mission : Identifie ce composant et classe-le avec précision.
    Tu dois OBLIGATOIREMENT respecter la hiérarchie suivante :
    {arbre_formatte}
    """
    try:
        reponse = ollama.chat(
            model='qwen2.5:7b',
            messages=[{'role': 'user', 'content': prompt}],
            format=ClassificationDatasheet.model_json_schema(), 
            options={'temperature': 0} 
        )
        return ClassificationDatasheet.model_validate_json(reponse['message']['content'])
    except Exception as e:
        print(f"Erreur d'appel IA : {e}")
        return None

# --- 3. LECTURE DU CSV ET ÉVALUATION ---
def lancer_evaluation(chemin_csv, limite_tests=10):
    print(f"📊 Chargement du fichier d'export : {chemin_csv}")
    
    succes_cat = 0
    succes_sous_cat = 0
    total_tests = 0
    
    with open(chemin_csv, mode='r', encoding='utf-8') as f:
        # Ton fichier utilise le point-virgule (;) comme délimiteur
        lecteur = csv.DictReader(f, delimiter=';')
        
        # Outils de diagnostic : affiche les colonnes détectées pour t'aider
        print(f"🔍 Colonnes trouvées dans ton CSV : {lecteur.fieldnames}\n")
        
        for ligne in lecteur:
            if total_tests >= limite_tests:
                break
                
            # ⚠️ AJUSTEMENT : Remplace les noms entre crochets par les vrais noms de tes colonnes CSV !
            # Exemple : si ta colonne s'appelle 'Designation', mets ligne['Designation']
            nom_composant = ligne.get('MPN', 'Inconnu')
            vraie_cat = ligne.get('Category', '')
            vraie_sous_cat = ligne.get('Subcategory', '')
            print(f"🧪 Test n°{total_tests + 1} : {nom_composant}")
            
            # On envoie le nom/description du composant à l'IA pour voir si elle devine la bonne catégorie
            prediction = classer_composant(nom_composant)
            
            if prediction:
                print(f"   [Attendu] Catégorie : {vraie_cat} | Sous-Catégorie : {vraie_sous_cat}")
                print(f"   [IA]      Catégorie : {prediction.categorie} | Sous-Catégorie : {prediction.sous_categorie}")
                
                # Vérification de la catégorie
                if str(prediction.categorie).strip().lower() == str(vraie_cat).strip().lower():
                    succes_cat += 1
                
                # Vérification de la sous-catégorie
                if str(prediction.sous_categorie).strip().lower() == str(vraie_sous_cat).strip().lower():
                    succes_sous_cat += 1
                    print("   ✅ Parfait !")
                else:
                    print("   ❌ Écart détecté")
                    
                print(f"   🧠 Raisonnement IA : {prediction.justification}\n")
            
            total_tests += 1

    # --- RÉSULTATS FINAUX ---
    if total_tests > 0:
        print("="*40)
        print("📈 BILAN DU TEST AUTOMATIQUE")
        print("="*40)
        print(f"Nombre de composants testés : {total_tests}")
        print(f"Précision Catégories        : {(succes_cat/total_tests)*100:.1f}% ({succes_cat}/{total_tests})")
        print(f"Précision Sous-catégories   : {(succes_sous_cat/total_tests)*100:.1f}% ({succes_sous_cat}/{total_tests})")

# --- Lancement du script ---
if __name__ == "__main__":
    # Le fichier CSV que tu viens de téléverser
    fichier_target = "components_stock-export.csv"
    
    if os.path.exists(fichier_target):
        # On commence par tester sur 5 lignes pour vérifier que tout fonctionne bien
        lancer_evaluation(fichier_target, limite_tests=5)
    else:
        print(f"Impossible de trouver le fichier {fichier_target}. Vérifie son emplacement.")