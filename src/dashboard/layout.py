"""
Définition du layout (structure HTML) de l'application Dash.

Ce module importe l'objet `app` et les figures statiques depuis
`app.py` et définit la structure visuelle de la page.
"""

from dash import dcc, html
# On importe les variables nécessaires depuis notre module app.py
from src.dashboard.app import app, fig_total_par_an, df 

# --- Définition du Layout ---

# Style pour les boîtes des KPIs
kpi_box_style = {
    'border': '1px solid #ddd', 
    'padding': '10px', 
    'textAlign': 'center', 
    'borderRadius': '5px',
    'backgroundColor': '#f9f9f9'
}

# Assigne la structure HTML à la propriété 'layout' de l'app
app.layout = html.Div(children=[
    
    html.H1(children='Dashboard des Accidents de Vélo en France', style={'textAlign': 'center'}),

    # --- 1. Graphique Statique (Évolution annuelle) ---
    html.Div(className='row', style={'marginBottom': '20px'}, children=[
        dcc.Graph(
            id='static-bar-chart-year',
            figure=fig_total_par_an # Figure statique créée dans app.py
        )
    ]),

    # --- 2. Panneau de Contrôle (Filtres) ---
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

    # --- 3. KPIs (Indicateurs clés dynamiques) ---
    html.Div(className='row', style={'marginBottom': '20px'}, children=[
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Total Accidents (sur l'année)"),
            html.H4(id='kpi-total-accidents') # ID pour le callback
        ]),
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Morts (sur l'année)"),
            html.H4(id='kpi-total-killed') # ID pour le callback
        ]),
        html.Div(className='four columns', style=kpi_box_style, children=[
            html.H3("Blessés Graves (sur l'année)"),
            html.H4(id='kpi-total-serious') # ID pour le callback
        ]),
    ]),

    # --- 4. Zone des Graphiques Dynamiques ---
    html.Div(className='row', children=[
        
        # Colonne de Gauche (Heatmap)
        html.Div(className='seven columns', children=[
            dcc.Graph(id='heatmap-graph') # ID pour le callback
        ]),
        
        # Colonne de Droite (Onglets)
        html.Div(className='five columns', children=[
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Par Heure', children=[
                    dcc.Graph(id='hist-hour-graph') 
                ]),
                dcc.Tab(label='Par Gravité', children=[
                    dcc.Graph(id='hist-grav-graph') 
                ]),
                dcc.Tab(label='Par Luminosité', children=[
                    dcc.Graph(id='hist-lum-graph') 
                ]),
            ])
        ])
    ])
])