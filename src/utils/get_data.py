import requests
import os

# --- Configuration des chemins ---

# On garde le lien de l'API, même s'il est capricieux.
# L'important est de montrer quel lien on a essayé d'utiliser.
DATA_URL = "https://opendata.koumoul.com/api/v2/datasets/accidents-velos/exports/csv?limit=-1&use_labels=true&timezone=Europe/Berlin"

# On utilise le chemin absolu (3 niveaux plus haut)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAVE_DIR = os.path.join(BASE_DIR, 'data', 'raw')
SAVE_PATH = os.path.join(SAVE_DIR, 'accidentsVelo-full.csv')


def get_data():
    """
    Télécharge les données si elles ne sont pas déjà présentes localement.
    """
    
    # --- LA PARTIE IMPORTANTE ---
    # 1. Vérifier si le fichier existe DÉJÀ.
    if os.path.exists(SAVE_PATH):
        print(f"Le fichier '{SAVE_PATH}' existe déjà.")
        print("Saut du téléchargement.")
        return  # On quitte la fonction
    
    # 2. Si le fichier n'existe pas, on tente le téléchargement
    print(f"Fichier non trouvé. Tentative de téléchargement depuis {DATA_URL}...")
    
    try:
        response = requests.get(DATA_URL, stream=True)
        response.raise_for_status() # Plante si erreur (404, 500...)

        os.makedirs(SAVE_DIR, exist_ok=True) # Crée le dossier s'il n'existe pas

        print(f"Sauvegarde en cours dans {SAVE_PATH}...")
        with open(SAVE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): 
                f.write(chunk)
        
        print("\n--- Téléchargement terminé avec succès! ---")

    except requests.exceptions.RequestException as e:
        print(f"ERREUR: Le téléchargement a échoué.")
        print(f"Raison : {e}")
        print("\nIMPORTANT: Veuillez télécharger le fichier manuellement depuis")
        print("https://opendata.koumoul.com/datasets/accidents-velos")
        print(f"et le placer dans le dossier 'data/raw/' sous le nom 'accidentsVelo-full.csv'")

if __name__ == "__main__":
    get_data()