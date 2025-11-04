import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os

# --- 1. Configuration et Chargement des données ---

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 

px.set_mapbox_access_token("pk.eyJ1IjoicGxvdGx5bWFwYnB4IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.ZIKYUdzeGtoLjTLFnF-eXQ")

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

# --- Traduction des Codes (Corrigée) ---
grav_mapping = {
    1.0: 'Indemne',
    2.0: 'Tué',
    3.0: 'Blessé Grave (Hospitalisé)',
    4.0: 'Blessé Léger'
}
lum_mapping = {
    1.0: 'Plein jour',
    2.0: 'Crépuscule ou aube',
    3.0: 'Nuit sans éclairage public',
    4.0: 'Nuit avec éclairage éteint',
    5.0: 'Nuit avec éclairage allumé'
}
df['grav_label'] = df['grav'].map(grav_mapping).fillna('Non défini')
df['lum_label'] = df['lum'].map(lum_mapping).fillna('Non défini')

print("Données nettoyées et mappées chargées.")

# --- 2. Création du Graphique Statique (indépendant) ---
df_accidents_par_an = df.groupby('year').size().reset_index(name='count')
fig_total_par_an = px.bar(
    df_accidents_par_an,
    x='year',
    y='count',
    title="Évolution du nombre total d'accidents de vélo par an"
)
fig_total_par_an.update_layout(xaxis_title="Année", yaxis_title="Nombre d'accidents")


# --- 3. Définition du Layout (la structure de la page) ---

kpi_box_style = {
    'border': '1px solid #ddd', 
    'padding': '10px', 
    'textAlign': 'center', 
    'borderRadius': '5px',
    'backgroundColor': '#f9f9f9'
}

app.layout = html.Div(children=[
    
    html.H1(children='Dashboard des Accidents de Vélo en France', style={'textAlign': 'center'}),

    # --- 1. Graphique Statique (La Frise) ---
    html.Div(className='row', style={'marginBottom': '20px'}, children=[
        dcc.Graph(
            id='static-bar-chart-year',
            figure=fig_total_par_an
        )
    ]),

    # --- 2. KPIs (Les Chiffres) ---
    html.Div(className='row', style={'marginBottom': '20px'}, children=[
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Total Accidents (sur l'année)"),
            html.H4(id='kpi-total-accidents')
        ]),
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Tués (sur l'année)"),
            html.H4(id='kpi-total-killed')
        ]),
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Blessés Graves (sur l'année)"),
            html.H4(id='kpi-total-serious')
        ]),
    ]),

    # --- 3. Panneau de Contrôle (Filtres) ---
    html.Div([
        html.Hr(),
        html.Label('Sélectionner une année pour filtrer tous les graphiques ci-dessous :'),
        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].max(),
            marks={str(year): str(year) for year in df['year'].unique()},
            step=None
        ),
    ], style={'padding': '20px'}),

    # --- 4. Zone des Graphiques Dynamiques ---
    html.Div(className='row', children=[
        
        html.Div(className='seven columns', children=[
            dcc.Graph(id='heatmap-graph') # La Heatmap
        ]),
        
        html.Div(className='five columns', children=[
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Par Heure', children=[
                    dcc.Graph(id='hist-hour-graph') # Histo (bien pour les heures)
                ]),
                dcc.Tab(label='Par Gravité', children=[
                    dcc.Graph(id='hist-grav-graph') # Donut (bien pour les catégories)
                ]),
                dcc.Tab(label='Par Luminosité', children=[
                    dcc.Graph(id='hist-lum-graph') # Donut (bien pour les catégories)
                ]),
            ])
        ])
    ])
])

# --- 4. Callbacks (Pour la dynamique) ---

@app.callback(
    [Output('kpi-total-accidents', 'children'),
     Output('kpi-total-killed', 'children'),
     Output('kpi-total-serious', 'children'),
     Output('heatmap-graph', 'figure'),
     Output('hist-hour-graph', 'figure'),
     Output('hist-grav-graph', 'figure'),
     Output('hist-lum-graph', 'figure')],
    [Input('year-slider', 'value')]
)
def update_dynamic_graphs(selected_year):
    print(f"Mise à jour pour l'année : {selected_year}")
    
    df_filtered = df[df['year'] == selected_year]
    
    if df_filtered.empty:
        empty_fig = {'layout': {'title': 'Pas de données pour cette année'}}
        return "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig

    total_accidents = len(df_filtered)
    total_killed = df_filtered[df_filtered['grav'] == 2.0].shape[0]
    total_serious = df_filtered[df_filtered['grav'] == 3.0].shape[0]

    if len(df_filtered) > 5000:
        df_sample = df_filtered.sample(n=5000, random_state=42)
    else:
        df_sample = df_filtered

    fig_map = px.density_map(
        df_sample, lat="lat", lon="long", radius=10,
        title=f"Zones de chaleur ({selected_year})",
        zoom=5, center={"lat": 46.603354, "lon": 1.888334}
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    fig_hour = px.histogram(df_filtered, x='hour', nbins=24, title="Par Heure")
    
    # --- CORRECTION DE L'ERREUR ---
    order_grav = ['Tué', 'Blessé Grave (Hospitalisé)', 'Blessé Léger', 'Indemne', 'Non défini']
    fig_grav = px.pie(
        df_filtered, 
        names='grav_label', 
        title="Par Gravité", 
        hole=0.4,
        # On dit à Plotly comment trier les labels AVANT de faire le graphe
        category_orders={'grav_label': order_grav} 
    )
    # On enlève la ligne qui faisait planter
    fig_grav.update_traces(textposition='inside', textinfo='percent+label')

    # --- CORRECTION APPLIQUÉE AUSSI ICI ---
    order_lum = ['Plein jour', 'Crépuscule ou aube', 'Nuit avec éclairage allumé', 'Nuit sans éclairage public', 'Nuit avec éclairage éteint', 'Non défini']
    fig_lum = px.pie(
        df_filtered, 
        names='lum_label', 
        title="Par Luminosité", 
        hole=0.4,
        category_orders={'lum_label': order_lum}
    )
    fig_lum.update_traces(textposition='inside', textinfo='percent+label')
    
    return (f"{total_accidents:,}",
            f"{total_killed:,}", 
            f"{total_serious:,}", 
            fig_map, 
            fig_hour, 
            fig_grav, 
            fig_lum)

# --- 5. Lancement du serveur ---
if __name__ == '__main__':
    app.run(debug=True)