"""
Script de nettoyage des données brutes.

Ce script lit le fichier CSV brut 'accidentsVelo-full.csv', 
sélectionne les colonnes pertinentes, nettoie les données 
(types, valeurs manquantes) et sauvegarde le résultat 
dans 'data/cleaned/accidents_cleaned.csv'.
"""

import pandas as pd
import os
from typing import List

# --- Configuration ---

# Chemins absolus pour la robustesse
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'accidentsVelo-full.csv')
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned', 'accidents_cleaned.csv')

# Colonnes à extraire du fichier CSV brut
COLUMNS_TO_KEEP: List[str] = [
    'Num_Acc',  
    'date',     
    'hrmn',     
    'lat',      
    'long',     
    'age',      
    'grav',     
    'sexe',     
    'atm',      
    'lum',      
    'dep',
    'larrout'   # Largeur de la route (pour l'histogramme)
]

def clean_data():
    """
    Fonction principale de nettoyage et de transformation des données.
    """
    print(f"Début du nettoyage... Lecture de {RAW_DATA_PATH}")

    try:
        df = pd.read_csv(RAW_DATA_PATH, sep=',', low_memory=False)
    except FileNotFoundError:
        print(f"ERREUR: Fichier non trouvé à {RAW_DATA_PATH}")
        print("Veuillez d'abord exécuter le script de récupération des données.")
        return
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du CSV : {e}")
        return

    # 1. Sélection des colonnes
    df_cleaned = df[COLUMNS_TO_KEEP].copy()

    # 2. Nettoyage et conversion des types
    
    df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], errors='coerce')
    df_cleaned['lat'] = pd.to_numeric(df_cleaned['lat'], errors='coerce')
    df_cleaned['long'] = pd.to_numeric(df_cleaned['long'], errors='coerce')
    
    # Extraction de l'heure (0-23) depuis le format 'HH:MM'
    df_cleaned['hour'] = pd.to_datetime(df_cleaned['hrmn'], format='%H:%M', errors='coerce').dt.hour
    
    # Nettoyage de 'larrout' (Largeur de route)
    # Conversion en numérique, en gérant les virgules décimales (ex: '6,5')
    df_cleaned['larrout'] = pd.to_numeric(
        df_cleaned['larrout'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )

    # Suppression de la colonne 'hrmn' originale, maintenant inutile
    df_cleaned = df_cleaned.drop(columns=['hrmn'])

    # 3. Suppression des lignes avec données invalides ou manquantes
    initial_rows = len(df_cleaned)
    
    # Définition des colonnes critiques pour l'analyse
    critical_columns = ['date', 'lat', 'long', 'age', 'hour', 'larrout']
    df_cleaned = df_cleaned.dropna(subset=critical_columns)
    
    # Suppression des aberrations géographiques (points à 0,0)
    df_cleaned = df_cleaned[df_cleaned['lat'] != 0]
    
    # Suppression des largeurs de route "0" (considérées comme données manquantes)
    df_cleaned = df_cleaned[df_cleaned['larrout'] > 0]
    
    print(f"Suppression de {initial_rows - len(df_cleaned)} lignes avec données manquantes ou invalides.")

    # 4. Conversion finale des types
    df_cleaned['age'] = df_cleaned['age'].astype(int)
    df_cleaned['hour'] = df_cleaned['hour'].astype(int)

    # 5. Sauvegarde du fichier nettoyé
    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    df_cleaned.to_csv(CLEANED_DATA_PATH, index=False, encoding='utf-8')
    
    print(f"Nettoyage terminé. Fichier sauvegardé dans {CLEANED_DATA_PATH}")

if __name__ == "__main__":
    clean_data()