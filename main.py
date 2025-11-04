import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os

# --- 1. Configuration et Chargement des données ---

# Feuille de style externe pour avoir des colonnes (row, columns)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 

px.set_mapbox_access_token("pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.ZIKYUdzeGtoLjTLFnF-eXQ")

# --- 2. Chargement des données ---
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

# --- 3. Définition du Layout (la structure de la page) ---

# Styles pour les boîtes des KPIs
kpi_box_style = {
    'border': '1px solid #ddd', 
    'padding': '10px', 
    'textAlign': 'center', 
    'borderRadius': '5px'
}

app.layout = html.Div(children=[
    
    # Titre
    html.H1(children='Dashboard des Accidents de Vélo en France', style={'textAlign': 'center'}),

    # --- KPIs (Indicateurs Clés) ---
    html.Div(className='row', style={'marginBottom': '20px'}, children=[
        
        # Boîte 1
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Total Accidents"),
            html.H4(id='kpi-total-accidents') # ID pour le callback
        ]),
        
        # Boîte 2
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Tués"),
            html.H4(id='kpi-total-killed') # ID pour le callback
        ]),
        
        # Boîte 3
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Blessés Graves"),
            html.H4(id='kpi-total-serious') # ID pour le callback
        ]),
    ]),

    # --- Panneau de Contrôle (Filtres) ---
    html.Div([
        html.Label('Sélectionner une année :'),
        dcc.Slider(
            id='year-slider',  # ID pour le callback
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].max(),
            marks={str(year): str(year) for year in df['year'].unique()},
            step=None
        ),
    ], style={'padding': '20px'}),

    # --- Zone des Graphiques (en 2 colonnes) ---
    html.Div(className='row', children=[
        
        # Colonne de Gauche (Heatmap)
        html.Div(className='seven columns', children=[
            dcc.Graph(id='heatmap-graph') # ID pour le callback
        ]),
        
        # Colonne de Droite (Onglets avec Histos)
        html.Div(className='five columns', children=[
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Par Heure', children=[
                    dcc.Graph(id='hist-hour-graph') # ID pour le callback
                ]),
                dcc.Tab(label='Par Météo', children=[
                    dcc.Graph(id='hist-weather-graph') # ID pour le callback
                ]),
                dcc.Tab(label='Par Âge', children=[
                    dcc.Graph(id='hist-age-graph') # ID pour le callback
                ]),
            ])
        ])
    ])
])

# --- 4. Callbacks (Pour la dynamique) ---

@app.callback(
    # On met à jour 7 choses en même temps
    [Output('kpi-total-accidents', 'children'),
     Output('kpi-total-killed', 'children'),
     Output('kpi-total-serious', 'children'),
     Output('heatmap-graph', 'figure'),
     Output('hist-hour-graph', 'figure'),
     Output('hist-weather-graph', 'figure'),
     Output('hist-age-graph', 'figure')],
    [Input('year-slider', 'value')] # Le seul déclencheur
)
def update_dashboard(selected_year):
    print(f"Mise à jour pour l'année : {selected_year}")
    
    # 1. Filtrer les données
    df_filtered = df[df['year'] == selected_year]
    
    # 2. Gérer le cas où il n'y a pas de données
    if df_filtered.empty:
        empty_fig = {'layout': {'title': 'Pas de données pour cette année'}}
        return "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig

    # 3. Calculer les KPIs
    # Note: D'après les données standard, grav=2 (Tué), grav=3 (Blessé grave/hospitalisé)
    total_accidents = len(df_filtered)
    total_killed = df_filtered[df_filtered['grav'] == 2].shape[0]
    total_serious = df_filtered[df_filtered['grav'] == 3].shape[0]

    # 4. Échantillonner pour la heatmap
    if len(df_filtered) > 5000:
        df_sample = df_filtered.sample(n=5000, random_state=42)
    else:
        df_sample = df_filtered

    # 5. Créer les graphiques
    fig_map = px.density_map(
        df_sample, lat="lat", lon="long", radius=10,
        title=f"Zones de chaleur ({selected_year})",
        zoom=5, center={"lat": 46.603354, "lon": 1.888334}
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    fig_hour = px.histogram(df_filtered, x='hour', nbins=24, title="Par Heure")
    fig_weather = px.histogram(df_filtered, x='atm', title="Par Météo")
    fig_age = px.histogram(df_filtered, x='age', nbins=20, title="Par Tranche d'Âge")

    # 6. Renvoyer toutes les valeurs (dans le bon ordre)
    return (f"{total_accidents:,}", # Format avec séparateur de milliers
            f"{total_killed:,}", 
            f"{total_serious:,}", 
            fig_map, 
            fig_hour, 
            fig_weather, 
            fig_age)

# --- 5. Lancement du serveur ---
if __name__ == '__main__':
    app.run(debug=True)