import json
from pypdf import PdfReader
import ollama
from pydantic import BaseModel, Field
from typing import Literal, Dict

# --- 1. CONFIGURATION : HIÉRARCHIE & CRITÈRES ---
HIERARCHIE = {
    "circuitProtection": ["ESD_TVS", "fuseHolders", "fuses"],
    "connector": ["Dupont", "JST", "powerJacks", "pinHeader_pinSocket"],
    "electromechanical": ["motors", "relays"],
    "embeddedSolutions": ["computing", "developmentKits", "sensorModules", "communicationRF"],
    "passiveComponents": ["capacitors", "inductors", "potentiometers", "resistors", "signalTransformers", "quartz"],
    "power": ["AC-DC_Converters", "DC-DC_Converters"],
    "semiconductors": ["diodes", "embeddedProcessors", "integratedCircuits", "memoryICs", "powerManagementICs", "wireless_RFSemiconductors", "transistors", "gateDriver", "amplifier", "buffer", "gpioExpander", "ledDriver", "transceiverRF", "transceiverEth", "motorDriver"],
    "sensors": ["audio", "current", "encoders", "magnetic", "pressure", "proximity", "temperature", "IMU"],
    "thermalManagement": ["fans", "heatSinks"],
    "wireCables": ["cableAssemblies", "multiConductorCables"],
    "tools": ["soldering"],
    "optoelectronic": ["LED", "IR", "phototransistor"]
}

CRITERES_TECHNIQUES = {
    "ESD_TVS": ["Tension de tenue (V)", "Tension de clampage (V)", "Puissance crête (W)", "Capacité parasite (pF)", "Boîtier"],
    "fuseHolders": ["Type de fusible", "Courant max (A)", "Tension max (V)", "Montage"],
    "fuses": ["Courant nominal (A)", "Tension nominale (V)", "Pouvoir de coupure (kA)", "Type"],
    "Dupont": ["Nombre de broches", "Pas (mm)", "Genre", "Courant par broche (A)", "Tension max (V)", "Montage"],
    "JST": ["Nombre de broches", "Pas (mm)", "Genre", "Courant par broche (A)", "Tension max (V)", "Montage"],
    "powerJacks": ["Nombre de broches", "Pas (mm)", "Genre", "Courant par broche (A)", "Tension max (V)", "Montage"],
    "pinHeader_pinSocket": ["Nombre de broches", "Pas (mm)", "Genre", "Courant par broche (A)", "Tension max (V)", "Montage"],
    "motors": ["Type", "Tension nominale (V)", "Courant nominal (A)", "Couple", "Vitesse (RPM)", "Angle par pas"],
    "relays": ["Tension de bobine (V)", "Courant bobine (mA)", "Tension de commutation max (V)", "Courant de commutation max (A)", "Nombre de pôles"],
    "computing": ["Processeur", "Fréquence (MHz)", "RAM (Go)", "Stockage", "Nombre de GPIO", "Interfaces"],
    "developmentKits": ["Microcontrôleur", "Tension logique (V)", "Interfaces", "Connectique embarquée"],
    "sensorModules": ["Type de capteur", "Interface", "Tension d'alimentation (V)", "Plage de mesure", "Résolution"],
    "communicationRF": ["Protocole", "Fréquence (MHz)", "Puissance de sortie (dBm)", "Sensibilité (dBm)", "Antenne"],
    "capacitors": ["Capacité (µF/pF)", "Tension nominale (V)", "Diélectrique", "Tolérance (%)", "ESR (Ω)"],
    "inductors": ["Inductance (µH/mH)", "Courant saturé (A)", "Résistance DC (Ω)", "Fréquence de résonance (MHz)"],
    "potentiometers": ["Résistance (Ω)", "Type", "Nombre de tours", "Tolérance (%)"],
    "resistors": ["Résistance (Ω)", "Puissance (W)", "Tolérance (%)", "Coefficient de température"],
    "signalTransformers": ["Rapport de transformation", "Inductance primaire (µH)", "Plage de fréquence (Hz)"],
    "quartz": ["Fréquence (MHz)", "Capacité de charge (pF)", "Tolérance de fréquence (ppm)", "ESR (Ω)"],
    "AC-DC_Converters": ["Tension d'entrée (V AC)", "Tension de sortie (V DC)", "Courant de sortie (A)", "Puissance (W)", "Rendement (%)", "Isolation"],
    "DC-DC_Converters": ["Tension d'entrée mini/maxi (V)", "Tension de sortie (V)", "Courant sortie (A)", "Rendement (%)", "Fréquence de découpage (kHz)"],
    "diodes": ["Tension inverse max (Vrrm)", "Courant direct moyen (If)", "Tension de seuil (Vf)", "Type"],
    "embeddedProcessors": ["Architecture", "Fréquence max (MHz)", "Flash", "RAM", "Nombre de broches / GPIO"],
    "integratedCircuits": ["Fonction principale", "Tension d'alimentation (V)", "Boîtier", "Courant de repos"],
    "memoryICs": ["Type", "Capacité", "Interface", "Tension (V)"],
    "powerManagementICs": ["Fonction", "Tension entrée/sortie (V)", "Courant max (A)", "Courant de repos"],
    "wireless_RFSemiconductors": ["Fréquence (GHz)", "Bande passante (MHz)", "Type", "Gain (dB)", "Tension"],
    "transistors": ["Type", "Vce/Vds max (V)", "Ic/Id max (A)", "Vgs(th) (V)", "Hfe ou Rds(on) (Ω)"],
    "gateDriver": ["Tension de sortie (V)", "Courant de pic (A)", "Nombre de canaux", "Temps de montée/descente (ns)"],
    "amplifier": ["Type", "Bande passante (MHz)", "Tension d'offset (mV)", "Alimentation (V)"],
    "buffer": ["Tension entrée/sortie (V)", "Courant de sortie (mA)", "Délai de propagation (ns)"],
    "gpioExpander": ["Nombre d'I/O", "Interface", "Tension logique (V)", "Mode"],
    "ledDriver": ["Nombre de canaux", "Courant par canal (mA)", "Tension d'alimentation (V)", "Interface de commande"],
    "transceiverRF": ["Fréquence (GHz)", "Débit binaire (Mbps)", "Modulation", "Puissance TX (dBm)", "Sensibilité RX (dBm)"],
    "transceiverEth": ["Standard", "Interface", "Tension (V)", "Température"],
    "motorDriver": ["Tension d'alimentation (V)", "Courant continu maximal (A)", "Pic de courant (A)", "Nombre de moteurs", "Logique de commande"],
    "audio": ["Sensibilité (dBV/Pa)", "Bande passante (Hz)", "Rapport signal/bruit (dB)", "Impédance (Ω)"],
    "current": ["Type", "Plage de courant (A)", "Sensibilité (mV/A)", "Sortie"],
    "encoders": ["Type", "Résolution", "Sortie", "Tension"],
    "magnetic": ["Plage de mesure", "Résolution", "Interface", "Tension"],
    "pressure": ["Plage de pression", "Précision (%)", "Type de sortie"],
    "proximity": ["Distance de détection (mm)", "Technologie", "Sortie"],
    "temperature": ["Plage de mesure (°C)", "Précision (±°C)", "Interface", "Tension"],
    "IMU": ["Axes", "Plage de mesure", "Interface", "Tension", "Débit de données"],
    "fans": ["Tension (V)", "Courant (A)", "Débit d'air (CFM)", "Bruit (dBA)", "Vitesse (RPM)", "Type de roulement"],
    "heatSinks": ["Résistance thermique (°C/W)", "Matériau", "Dimensions", "Type de fixation"],
    "cableAssemblies": ["Longueur", "Connecteurs aux extrémités", "Nombre de conducteurs", "Type de fils (AWG)"],
    "multiConductorCables": ["Section", "Nombre de conducteurs", "Isolation", "Tension max (V)"],
    "soldering": ["Type", "Puissance (W)", "Plage de température (°C)", "Type de panne"],
    "LED": ["Couleur", "Tension directe (Vf)", "Intensité lumineuse (mcd)", "Angle de vue (°)", "Puissance (W)"],
    "IR": ["Longueur d'onde (nm)", "Tension directe (V)", "Angle de vue", "Portée (m)"],
    "phototransistor": ["Longueur d'onde de pic (nm)", "Sensibilité (µA/lux)", "Tension collecteur-émetteur (V)", "Courant obscur (µA)"]
}

ToutesCategories = tuple(HIERARCHIE.keys())
ToutesSousCategories = tuple([item for sublist in HIERARCHIE.values() for item in sublist])

# --- 2. MODÈLE PYDANTIC ---
class ExtractionComposant(BaseModel):
    justification: str = Field(description="Explication de la fonction du composant.")
    categorie: Literal[ToutesCategories]
    sous_categorie: Literal[ToutesSousCategories]
    caracteristiques: Dict[str, str] = Field(description="Dictionnaire contenant les valeurs techniques extraites.")

# --- 3. FONCTIONS ---
def lire_pdf(chemin_fichier, max_pages=10):
    try:
        reader = PdfReader(chemin_fichier)
        texte = ""
        # On lit les 2 premières pages pour choper les specs électriques
        for page in reader.pages[:max_pages]:
            texte += page.extract_text() + "\n"
        return texte
    except Exception as e:
        print(f"❌ Erreur de lecture du PDF : {e}")
        return None

def analyser_datasheet(texte_pdf):
    arbre_formatte = json.dumps(HIERARCHIE, indent=2)
    criteres_formattes = json.dumps(CRITERES_TECHNIQUES, indent=2)
    
    prompt = f"""
    Voici les premières pages d'une datasheet :
    {texte_pdf[:3000]}
    
    Mission :
    1. Identifie la 'categorie' et la 'sous_categorie' en respectant cette hiérarchie :
    {arbre_formatte}
    
    2. Une fois la sous_categorie choisie, regarde cette liste de critères :
    {criteres_formattes}
    
    3. Extrais les valeurs de la datasheet correspondant UNIQUEMENT aux critères de ta sous_categorie.
    Place ces valeurs dans le dictionnaire 'caracteristiques'. Si une valeur est introuvable, écris "N/A". prends le temps d'étudier les tableau les colonnes values et les schémas pour trouver les valeurs.  """

    
    print("🤖 Analyse technique en cours par l'IA...")
    try:
        reponse = ollama.chat(
            model='qwen2.5:7b',
            messages=[{'role': 'user', 'content': prompt}],
            format=ExtractionComposant.model_json_schema(),
            options={'temperature': 0}
        )
        return ExtractionComposant.model_validate_json(reponse['message']['content'])
    except Exception as e:
        print(f"❌ Erreur d'analyse IA : {e}")
        return None

# --- 4. EXÉCUTION LOCALE ---
if __name__ == "__main__":
    # J'ai mis le nom du fichier que j'avais vu sur ta capture d'écran
    fichier_cible = "stm32wb55cc.pdf" 
    
    print(f"📄 Ouverture de {fichier_cible}...")
    texte_brut = lire_pdf(fichier_cible)
    
    if texte_brut:
        resultat = analyser_datasheet(texte_brut)
        if resultat:
            print("\n" + "="*40)
            print("🎯 RÉSULTAT DE L'EXTRACTION")
            print("="*40)
            print(f"🧠 Raisonnement : {resultat.justification}")
            print(f"📁 Classé dans  : {resultat.categorie} > {resultat.sous_categorie}")
            print("\n⚙️  Caractéristiques techniques :")
            for cle, valeur in resultat.caracteristiques.items():
                print(f"   - {cle} : {valeur}")