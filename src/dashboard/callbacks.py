"""
Définition des callbacks de l'application Dash.

Ce module importe l'objet `app` et le DataFrame `df` depuis `app.py`
et définit les fonctions qui rendent le dashboard interactif.
"""

import plotly.express as px
from dash.dependencies import Input, Output
from src.dashboard.app import app, df 
from typing import Tuple, Any
import pandas as pd

# Désactive l'avertissement SettingWithCopyWarning de Pandas,
# qui pourrait autrement se produire lors de filtrages successifs.
pd.options.mode.chained_assignment = None

@app.callback(
    [Output('kpi-total-accidents', 'children'),
     Output('kpi-total-killed', 'children'),
     Output('kpi-total-serious', 'children'),
     Output('heatmap-graph', 'figure'),
     Output('hist-larrout-graph', 'figure'),
     Output('hist-grav-graph', 'figure'),
     Output('hist-lum-graph', 'figure')],
    [Input('year-slider', 'value')]
)
def update_dynamic_graphs(selected_year: int) -> Tuple[str, str, str, Any, Any, Any, Any]:
    """
    Met à jour tous les graphiques dynamiques et KPIs en fonction de l'année sélectionnée.
    
    Args:
        selected_year (int): L'année choisie via le slider.
    
    Returns:
        Tuple[str, str, str, Any, Any, Any, Any]: Un tuple contenant les 7 sorties
        (3 KPIs textuels et 4 figures Plotly).
    """
    print(f"Mise à jour pour l'année : {selected_year}")
    
    # 1. Filtrer les données pour l'année sélectionnée
    df_filtered = df[df['year'] == selected_year]
    
    # 2. Gérer le cas où il n'y a pas de données pour cette année
    if df_filtered.empty:
        empty_fig = {'layout': {'title': 'Pas de données pour cette année'}}
        return "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig

    # 3. Calculer les KPIs
    total_accidents: int = len(df_filtered)
    total_killed: int = df_filtered[df_filtered['grav'] == 2.0].shape[0]
    total_serious: int = df_filtered[df_filtered['grav'] == 3.0].shape[0]

    # 4. Échantillonner pour la heatmap (pour la performance)
    if len(df_filtered) > 5000:
        df_sample = df_filtered.sample(n=5000, random_state=42)
    else:
        df_sample = df_filtered

    # 5. Création des graphiques dynamiques
    
    # Graphique 1 : Heatmap (Carte de chaleur)
    fig_map = px.density_mapbox(
        df_sample, lat="lat", lon="long", 
        radius=8,
        title=f"Répartition des accidents ({selected_year})",
        zoom=5, center={"lat": 46.603354, "lon": 1.888334},
        color_continuous_scale="OrRd", 
        mapbox_style="carto-positron" 
    )
    fig_map.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        coloraxis_colorbar_title_text="Densité"
    )

    # Graphique 2 : Vrai Histogramme (Largeur de route)
    # Filtre les valeurs extrêmes (>20m) pour une meilleure lisibilité
    df_filtered_larrout = df_filtered[df_filtered['larrout'] < 20]
    
    fig_larrout_hist = px.histogram(
        df_filtered_larrout, 
        x='larrout',
        nbins=40,
        title="Distribution par Largeur de Route (m)"
    )
    fig_larrout_hist.update_layout(
        xaxis_title="Largeur de la route (en mètres)",
        yaxis_title="Nombre d'accidents",
        showlegend=False,
        bargap=0.1
    )
    
    # Graphique 3 : Camembert (Gravité)
    order_grav = ['Tué', 'Blessé Grave (Hospitalisé)', 'Blessé Léger', 'Indemne', 'Non défini']
    fig_grav = px.pie(
        df_filtered, 
        names='grav_label', 
        title="Gravité des accidents", 
        category_orders={'grav_label': order_grav} 
    )
    fig_grav.update_traces(textposition='inside', textinfo='percent+label')

    # Graphique 4 : Camembert (Luminosité)
    order_lum = ['Plein jour', 'Crépuscule ou aube', 'Nuit avec éclairage allumé', 'Nuit sans éclairage public', 'Nuit avec éclairage éteint', 'Non défini']
    fig_lum = px.pie(
        df_filtered, 
        names='lum_label', 
        title="Luminosité lors des accidents", 
        category_orders={'lum_label': order_lum}
    )
    fig_lum.update_traces(textposition='inside', textinfo='percent+label')
    
    # 6. Renvoyer toutes les valeurs (dans le bon ordre)
    return (f"{total_accidents:,}",
            f"{total_killed:,}", 
            f"{total_serious:,}", 
            fig_map, 
            fig_larrout_hist,
            fig_grav, 
            fig_lum)