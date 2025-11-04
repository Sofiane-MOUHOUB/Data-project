import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os

# --- 1. Configuration et Chargement des données ---

px.set_mapbox_access_token("pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.ZIKYUdzeGtoLjTLFnF-eXQ")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned', 'accidents_cleaned.csv')

try:
    df = pd.read_csv(CLEANED_DATA_PATH)
except FileNotFoundError:
    print(f"ERREUR: Fichier nettoyé non trouvé à {CLEANED_DATA_PATH}")
    print("Veuillez d'abord lancer 'python src/utils/clean_data.py' pour le générer.")
    exit(1)

df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year

print("Données nettoyées chargées.")

# --- 2. Initialisation de l'application Dash ---
app = dash.Dash(__name__)
server = app.server

# --- 3. Définition du Layout (la structure de la page) ---

min_year = df['year'].min()
max_year = df['year'].max()

app.layout = html.Div(children=[
   
    html.H1(children='Dashboard des Accidents de Vélo en France'),
    html.Div(children='Analyse basée sur les données OpenData.'),

    # --- LE FILTRE DYNAMIQUE ---
    html.Div([
        html.Label('Sélectionner une année :'),
        dcc.Slider(
            id='year-slider',
            min=min_year,
            max=max_year,
            value=max_year,
            marks={str(year): str(year) for year in df['year'].unique()},
            step=None
        ),
    ], style={'padding': '20px'}),

    # --- La section des graphiques ---
    # Cette Div sera remplie par le callback
    html.Div(id='graphs-container')

])

# --- 4. Callbacks (Pour la dynamique) ---

@app.callback(
    Output('graphs-container', 'children'), # CIBLE
    Input('year-slider', 'value')           # SOURCE
)
def update_graphs(selected_year):
    print(f"Mise à jour des graphiques pour l'année : {selected_year}")
   
    # 1. Filtrer les données
    df_filtered = df[df['year'] == selected_year]
   
    # 2. Échantillonner pour la heatmap (sinon c'est trop lent)
    if len(df_filtered) > 5000:
        df_sample = df_filtered.sample(n=5000, random_state=42)
    else:
        df_sample = df_filtered
   
    # 3. Recréer les graphiques
   
    # Graphique 1 : Histogramme par Heure
    fig_hist_hour = px.histogram(
        df_filtered,
        x='hour',
        nbins=24,
        title=f"Répartition des accidents par heure ({selected_year})"
    )
    fig_hist_hour.update_layout(
        xaxis_title="Heure de la journée (0-23h)",
        yaxis_title="Nombre d'accidents"
    )

    # --- NOUVEAU GRAPHIQUE ---
    # Graphique 2 : Histogramme par Météo
    fig_hist_weather = px.histogram(
        df_filtered,
        x='atm',  # Colonne des conditions atmosphériques
        title=f"Répartition par conditions météo ({selected_year})"
    )
    fig_hist_weather.update_layout(
        xaxis_title="Conditions atmosphériques",
        yaxis_title="Nombre d'accidents"
    )

    # --- GRAPHIQUE MODIFIÉ ---
    # Graphique 3 : Heatmap (Carte de chaleur)
    fig_map = px.density_map( # <-- REMPLACÉ
        df_sample,
        lat="lat",
        lon="long",
        radius=10, # Rayon de la zone de "chaleur"
        title=f"Carte de chaleur des accidents ({selected_year}) - Échantillon de {len(df_sample)} points",
        zoom=5,
        center={"lat": 46.603354, "lon": 1.888334}
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    # 4. Renvoyer les nouveaux graphiques à la Div
    return [
        html.Div(className="graph-container", children=[
            html.H3("Quand ont lieu les accidents ?"),
            dcc.Graph(id='histogram-hour', figure=fig_hist_hour)
        ]),
       
        # --- AJOUTÉ AU LAYOUT ---
        html.Div(className="graph-container", children=[
            html.H3("Dans quelles conditions ?"),
            dcc.Graph(id='histogram-weather', figure=fig_hist_weather)
        ]),
       
        html.Div(className="graph-container", children=[
            html.H3("Où ont lieu les accidents ? (Heatmap)"),
            dcc.Graph(id='map-accidents', figure=fig_map)
        ])
    ]

# --- 5. Lancement du serveur ---
if __name__ == '__main__':
    app.run(debug=True)

