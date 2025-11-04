import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output 
import os

# --- 1. Configuration et Chargement des données ---

# Clé d'accès publique pour Mapbox (nécessaire pour le fond de carte)
px.set_mapbox_access_token("pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.ZIKYUdzeGtoLjTLFnF-eXQ")

# Chemin vers le fichier NETTOYÉ
# On part du principe que tu lances ce script depuis la racine du projet
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned', 'accidents_cleaned.csv')

# Charger les données propres
try:
    df = pd.read_csv(CLEANED_DATA_PATH)
except FileNotFoundError:
    print(f"ERREUR: Fichier nettoyé non trouvé à {CLEANED_DATA_PATH}")
    print("Veuillez d'abord lancer 'python src/utils/clean_data.py' pour le générer.")
    exit(1) 

# Conversion de la date (pour être sûr)
df['date'] = pd.to_datetime(df['date'])
# Créer une colonne 'année' pour le filtre
df['year'] = df['date'].dt.year

# --- Échantillonnage pour la carte ---
# On prend 5000 points pour que la carte soit fluide
df_sample = df.sample(n=5000, random_state=42) 

print("Données nettoyées chargées et échantillonnées.")

# --- 2. Création des Graphiques (Statiques) ---

# Graphique 1 : Histogramme des accidents par heure (Obligatoire 1)
fig_histogram_hour = px.histogram(
    df, 
    x='hour',
    nbins=24,
    title="Répartition des accidents de vélo par heure"
)
fig_histogram_hour.update_layout(
    xaxis_title="Heure de la journée (0-23h)",
    yaxis_title="Nombre d'accidents",
    bargap=0.1
)

# Graphique 2 : Carte des accidents (Obligatoire 2)
# On utilise px.scatter_map (version récente)
fig_map = px.scatter_map(
    df_sample, 
    lat="lat",
    lon="long",
    color="grav",  # Couleur selon la gravité
    hover_name="Num_Acc", 
    hover_data=["date", "age", "hour"], 
    title="Carte de 5000 accidents de vélo (échantillon)",
    zoom=5, 
    center={"lat": 46.603354, "lon": 1.888334} # Centre de la France
)
fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}) # Moins de marges

# --- 3. Initialisation de l'application Dash ---
app = dash.Dash(__name__)
server = app.server 

# --- 4. Définition du Layout (la structure de la page) ---
app.layout = html.Div(children=[
    
    # Un grand titre
    html.H1(children='Dashboard des Accidents de Vélo en France'),

    # Une petite description
    html.Div(children='''
        Analyse basée sur les données OpenData des accidents de vélo.
    '''),

    # Section pour l'histogramme
    html.Div(className="graph-container", children=[
        html.H3("Quand ont lieu les accidents ?"),
        dcc.Graph(
            id='histogram-hour',
            figure=fig_histogram_hour
        )
    ]),
    
    # Section pour la carte
    html.Div(className="graph-container", children=[
        html.H3("Où ont lieu les accidents ?"),
        dcc.Graph(
            id='map-accidents',
            figure=fig_map
        )
    ])
])

# --- 5. Callbacks (Pour la dynamique) ---
# ... (On ajoutera le callback ici) ...


# --- 6. Lancement du serveur ---
if __name__ == '__main__':
    # On utilise app.run() pour les versions récentes de Dash
    app.run(debug=True)