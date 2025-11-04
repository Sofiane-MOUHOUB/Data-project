import os

# --- Configuration des chemins ---

# On calcule le chemin absolu de la racine du projet
# (On est dans src/utils/, donc on remonte de 3 niveaux)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# On définit le chemin complet où le fichier DEVRAIT être
SAVE_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'accidentsVelo-full.csv')

# Lien de la page source, pour l'information
DATA_SOURCE_PAGE = "https://opendata.koumoul.com/datasets/accidents-velos"


def check_data_file():
    """
    Vérifie la présence du fichier de données brutes 'accidentsVelo-full.csv'.
    
    Si le fichier est présent, le script se termine avec succès.
    Si le fichier est manquant, affiche un message d'erreur clair.
    """
    
    # On vérifie si le fichier existe à l'endroit attendu
    if os.path.exists(SAVE_PATH):
        print(f"OK: Le fichier de données brutes est bien présent à : {SAVE_PATH}")
        return
    
    # Si le script arrive ici, c'est que le fichier est manquant
    print("=" * 50)
    print("ERREUR: Fichier de données brutes manquant.")
    print(f"Le fichier 'accidentsVelo-full.csv' n'a pas été trouvé dans le dossier 'data/raw/'.")
    print("\nAction requise :")
    print(f"1. Téléchargez le fichier manuellement depuis : {DATA_SOURCE_PAGE}")
    print(f"2. Placez-le dans le dossier : {os.path.join(BASE_DIR, 'data', 'raw')}")
    print("=" * 50)
    # On quitte le script avec un code d'erreur
    exit(1)


if __name__ == "__main__":
    # Permet de lancer ce script directement avec:
    # python src/utils/get_data.py
    check_data_file()