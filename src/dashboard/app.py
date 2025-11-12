"""
Module principal de l'application Dash.

Ce fichier est responsable de :
1. L'initialisation de l'objet `app` Dash.
2. Le chargement et la préparation des données (DataFrame).
3. La création des figures statiques (non-dépendantes des callbacks).
"""

import pandas as pd
import plotly.express as px
import dash
import os
from typing import Dict, Any

# --- 1. Initialisation de l'application ---

external_stylesheets: list[str] = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 
px.set_mapbox_access_token("pk.eyJ1IjoicGxvdGx5bWFwYnB4IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.ZIKYUdzeGtoLjTLFnF-eXQ")


# --- 2. Chargement et préparation des données ---

def load_and_prepare_data(csv_path: str) -> pd.DataFrame:
    """
    Charge les données nettoyées et applique les transformations nécessaires.
    
    Args:
        csv_path (str): Le chemin vers le fichier CSV nettoyé.
    
    Returns:
        pd.DataFrame: Le DataFrame prêt pour l'analyse.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"ERREUR: Fichier nettoyé non trouvé à {csv_path}")
        print("Veuillez d'abord lancer 'python src/utils/clean_data.py' pour le générer.")
        exit(1) 

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    grav_mapping: Dict[float, str] = {
        1.0: 'Indemne', 2.0: 'Tué', 3.0: 'Blessé Grave (Hospitalisé)', 4.0: 'Blessé Léger'
    }
    lum_mapping: Dict[float, str] = {
        1.0: 'Plein jour', 2.0: 'Crépuscule ou aube', 3.0: 'Nuit sans éclairage public',
        4.0: 'Nuit avec éclairage éteint', 5.0: 'Nuit avec éclairage allumé'
    }
    
    df['grav_label'] = df['grav'].map(grav_mapping).fillna('Non défini')
    df['lum_label'] = df['lum'].map(lum_mapping).fillna('Non défini')
    
    print("Données nettoyées et mappées chargées.")
    return df

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned', 'accidents_cleaned.csv')
df = load_and_prepare_data(CLEANED_DATA_PATH)


# --- 3. Création des figures statiques ---

def create_static_figures(data: pd.DataFrame) -> Any:
    """
    Crée le graphique d'évolution annuelle (statique).
    
    Args:
        data (pd.DataFrame): Le DataFrame complet.
    
    Returns:
        plotly.graph_objects.Figure: La figure du graphique.
    """
    df_accidents_par_an = data.groupby('year').size().reset_index(name='count')
    
    # --- CHANGEMENT DE px.area à px.line ---
    fig = px.line(
        df_accidents_par_an,
        x='year',
        y='count',
        title="Évolution du nombre total d'accidents de vélo par an"
    )
    fig.update_layout(
        xaxis_title="Année", 
        yaxis_title="Nombre d'accidents",
        xaxis = dict(dtick=1) 
    )
    return fig

# Crée le graphique au démarrage
fig_total_par_an = create_static_figures(df)