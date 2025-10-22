import pandas as pd
import os

# --- Configuration des chemins ---
# Définir le chemin de base du projet (là où se trouve .git)
# Ce script est dans src/utils, donc on remonte de deux niveaux
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'accidentsVelo-full.csv')
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned', 'accidents_cleaned.csv')

# --- Colonnes à conserver ---
# On ne garde que ce qui est utile pour le dashboard
# (identifiant, date, geo, et variables pour les graphiques/filtres)
COLUMNS_TO_KEEP = [
    'Num_Acc',  # Identifiant unique
    'date',     # Pour le filtre temporel
    'lat',      # Obligatoire pour la carte
    'long',     # Obligatoire pour la carte
    'age',      # Obligatoire pour l'histogramme
    'grav',     # Gravité (pour filtres/couleurs)
    'sexe',     # Sexe (pour filtres)
    'atm',      # Conditions atmosphériques (pour filtres)
    'lum',      # Luminosité (pour filtres)
    'dep',       # Département (pour filtres)
    'hrmn'
]

def clean_data():
    """
    Script principal pour nettoyer les données brutes des accidents de vélo.
    1. Lit les données brutes.
    2. Sélectionne les colonnes pertinentes.
    3. Nettoie et convertit les types de données (dates, nombres).
    4. Supprime les lignes avec des données critiques manquantes (geo, age).
    5. Sauvegarde le fichier nettoyé dans data/cleaned/.
    """
    print(f"Début du nettoyage... Lecture de {RAW_DATA_PATH}")

    # 1. Lire les données brutes
    # low_memory=False évite les avertissements sur les types mixtes

    try:
        df = pd.read_csv(RAW_DATA_PATH, sep=',', low_memory=False)
    except FileNotFoundError:
        print(f"ERREUR: Fichier non trouvé à {RAW_DATA_PATH}")
        print("Veuillez d'abord placer 'accidentsVelo-full.csv' dans le dossier 'data/raw/'.")
        return
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du CSV : {e}")
        return

    # 2. Sélectionner les colonnes pertinentes
    # On fait une copie pour éviter les avertissements (SettingWithCopyWarning)
    df_cleaned = df[COLUMNS_TO_KEEP].copy()

    # 3. Nettoyer et convertir les types de données
    
    # --- Date ---
    # Convertit la colonne 'date' en objet datetime. 
    # errors='coerce' transforme les dates invalides en 'NaT' (Not a Time)
    df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], errors='coerce')

    # --- Coordonnées Géographiques (lat, long) ---
    # Convertit en numérique. errors='coerce' transforme ce qui n'est pas un nombre en 'NaN'
    df_cleaned['lat'] = pd.to_numeric(df_cleaned['lat'], errors='coerce')
    df_cleaned['long'] = pd.to_numeric(df_cleaned['long'], errors='coerce')

    df_cleaned['hour'] = pd.to_datetime(df_cleaned['hrmn'], format='%H:%M', errors='coerce').dt.hour
    df_cleaned = df_cleaned.drop(columns=['hrmn'])

    # 4. Supprimer les lignes avec des données critiques manquantes
    
    # On supprime les lignes où la date, la lat/long ou l'âge sont manquants.
    # Un accident sans ces infos est inutile pour nos graphiques.
    initial_rows = len(df_cleaned)
    df_cleaned = df_cleaned.dropna(subset=['date', 'lat', 'long', 'age','hour'])
    
    # On supprime les coordonnées (0, 0) qui sont des valeurs "nulles" fréquentes
    df_cleaned = df_cleaned[df_cleaned['lat'] != 0]
    
    print(f"Suppression de {initial_rows - len(df_cleaned)} lignes avec données manquantes ou invalides.")

    # 5. Conversion finale des types
    
    # Maintenant que les 'NaN' sont partis, on peut convertir l'âge en entier
    df_cleaned['age'] = df_cleaned['age'].astype(int)
    df_cleaned['hour'] = df_cleaned['hour'].astype(int)

    # 6. Sauvegarder le fichier nettoyé
    
    # Assurer que le dossier 'data/cleaned' existe
    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    
    # index=False est crucial pour ne pas ajouter une colonne d'index inutile dans le CSV
    df_cleaned.to_csv(CLEANED_DATA_PATH, index=False, encoding='utf-8')
    
    print(f"Nettoyage terminé. Fichier sauvegardé dans {CLEANED_DATA_PATH}")
    print(f"Total des accidents conservés : {len(df_cleaned)}")

if __name__ == "__main__":
    # Permet de lancer ce script directement avec "python src/utils/clean_data.py"
    clean_data()