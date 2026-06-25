from pypdf import PdfReader
import ollama
from pydantic import BaseModel, Field
from typing import Literal
import json

# --- 1. LA HIÉRARCHIE (Miroir de ton fichier CSV) ---
# Ce dictionnaire lie chaque catégorie à ses sous-catégories exclusives.
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

# --- 2. VALIDATION PYDANTIC (Sécurité anti-fautes de frappe) ---
# On extrait dynamiquement les clés et les valeurs pour que Pydantic vérifie la syntaxe
ToutesCategories = tuple(HIERARCHIE.keys())
ToutesSousCategories = tuple([item for sublist in HIERARCHIE.values() for item in sublist])

CategorieType = Literal[ToutesCategories]
SousCategorieType = Literal[ToutesSousCategories]

class ClassificationDatasheet(BaseModel):
    justification: str = Field(description="Explication très brève de la fonction du composant.")
    categorie: CategorieType = Field(description="La catégorie principale choisie.")
    sous_categorie: SousCategorieType = Field(description="La sous-catégorie associée.")

# --- 3. LES FONCTIONS ---
def lire_pdf(chemin_fichier, max_pages=10):
    try:
        reader = PdfReader(chemin_fichier)
        texte = ""
        for page in reader.pages[:max_pages]:
            texte += page.extract_text() + "\n"
        return texte
    except Exception as e:
        print(f"❌ Erreur PDF : {e}")
        return None

def classer_composant(texte):
    # L'astuce est ici : on convertit le dictionnaire Python en texte lisible par l'IA
    arbre_formatte = json.dumps(HIERARCHIE, indent=2)
    
    prompt = f"""
    Voici la première page d'une datasheet :
    {texte}
    
    Mission : Identifie ce composant et classe-le avec précision pour se faire tu peux te baser sur les caractéristiques usuel des composants exemples ça parles d'inductances c'est plus facilement une bobine ect...
    Une fois que tu as la catégorie, je te conseil de chercher des synonimes et le vocabulaire propre au catégorie pour bien cerner le contours de celle ci et ensuite comme ça tu peux est plus précis dans ton classement 
    
    RÈGLE ABSOLUE : Tu dois OBLIGATOIREMENT respecter la hiérarchie suivante. 
    Si tu choisis une 'Catégorie', la 'Sous-catégorie' que tu sélectionnes DOIT faire partie de sa liste associée ci-dessous :
    
    {arbre_formatte}
    """
    
    print("🤖 Classification hiérarchique en cours...")
    reponse = ollama.chat(
        model='qwen2.5:7b',
        messages=[{'role': 'user', 'content': prompt}],
        format=ClassificationDatasheet.model_json_schema(), 
        options={'temperature': 0} 
    )
    
    return ClassificationDatasheet.model_validate_json(reponse['message']['content'])

# --- 4. EXÉCUTION ---
pdf_test = "test.pdf" # Remplace par ton PDF si besoin

texte_brut = lire_pdf(pdf_test)
if texte_brut:
    resultat = classer_composant(texte_brut)
    print("\n" + "="*40)
    print("🎯 RÉSULTAT DE LA CLASSIFICATION")
    print("="*40)
    print(f"🧠 Raisonnement : {resultat.justification}")
    print(f"📁 Catégorie    : {resultat.categorie}")
    print(f"📂 Sous-catég.  : {resultat.sous_categorie}")