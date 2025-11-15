# 🚴 Dashboard d'Analyse des Accidents de Vélo en France

Ce projet propose un dashboard interactif pour l'analyse des accidents de vélo en France, basé sur les données ouvertes (Open Data) de 2005 à 2023.

L'application est construite en Python en utilisant Dash et Plotly. Elle permet de visualiser l'évolution globale des accidents, puis de filtrer par année pour explorer les points chauds géographiques, la distribution des accidents par largeur de route, leur gravité et la luminosité ambiante.

## 🚀 User Guide

Ce guide décrit les étapes pour déployer et lancer l'application dashboard sur une autre machine.

### Prérequis

* Python 3.10+
* `git`
* Un navigateur web standard (Chrome, Firefox, etc.)

### Instructions d'installation

1.  **Cloner le dépôt :**
    Ouvrez un terminal et clonez le dépôt du projet.
    ```bash
    git clone https://github.com/Sofiane-MOUHOUB/Data-project.git
    cd Data-project
    ```

2.  **Installer les dépendances :**
    Le fichier `requirements.txt` contient tous les packages nécessaires.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Préparer les données :**
    Le dépôt inclut les données brutes. Vous devez exécuter le script de nettoyage une fois pour générer le fichier `accidents_cleaned.csv` qui sera utilisé par le dashboard.
    ```bash
    python src/utils/clean_data.py
    ```

4.  **Lancer le dashboard :**
    L'application est lancée via le point d'entrée `main.py`.
    ```bash
    python main.py
    ```

5.  **Accéder à l'application :**
    Ouvrez votre navigateur et allez à l'adresse indiquée dans le terminal (par défaut : `http://127.0.0.1:8050/`).

---

## 📊 Data

Le jeu de données utilisé pour ce projet est **"Accidents de Vélo"** (2005-2023).

Il est accessible en Open Data et est maintenu sur la plateforme Koumoul. Le fichier `data/raw/accidentsVelo-full.csv` est inclus dans ce dépôt pour garantir l'exécution hors-ligne, comme demandé par le cahier des charges.

* **Source Officielle :** [https://opendata.koumoul.com/datasets/accidents-velos](https://opendata.koumoul.com/datasets/accidents-velos)

---

## 💻 Developer Guide

L'application suit une structure modulaire pour séparer les responsabilités (logique applicative, layout, et interactivité), conformément aux bonnes pratiques de Dash.

### Architecture du Code

Le point d'entrée est `main.py`, qui se contente d'importer et de lancer l'application. La logique du dashboard est contenue dans le package `src/dashboard`.

* `src/dashboard/app.py` : Initialise l'instance `dash.Dash`, charge et prépare le DataFrame Pandas (`df`), et crée les graphiques statiques (le graphique en ligne de l'évolution annuelle).
* `src/dashboard/layout.py` : Définit la structure visuelle (HTML et composants `dcc`) de l'application. Il importe les figures statiques depuis `app.py`.
* `src/dashboard/callbacks.py` : Contient toute la logique interactive. Il définit la fonction `@app.callback` qui met à jour tous les graphiques dynamiques et les KPIs en fonction de l'entrée du `dcc.Slider`.
* `src/utils/` : Contient les scripts pour la vérification (`get_data.py`) et le nettoyage (`clean_data.py`) des données. Le script de nettoyage est crucial car il convertit les codes (ex: `grav = 1.0`) en labels lisibles (ex: "Indemne") et prépare la variable `larrout` pour l'histogramme.

### Diagramme d'architecture (Mermaid)

```mermaid
graph TD
    A[main.py] --> B(src/dashboard/app.py)
    A --> C(src/dashboard/layout.py)
    A --> D(src/dashboard/callbacks.py)
    
    C -- Importe app, fig_total --> B
    D -- Importe app, df --> B
    
    B -- Charge --> E(data/cleaned/accidents_cleaned.csv)
    F(src/utils/clean_data.py) -- Génère --> E
    F -- Lit --> G(data/raw/accidentsVelo-full.csv)


Rapport d'analyse

Ce dashboard a permis d'extraire plusieurs conclusions clés sur les accidents de vélo en France (période 2010-2023).

1. Avertissement sur les données (2018-2019)
L'analyse de l'évolution annuelle (graphique en ligne) montre une chute drastique des accidents en 2018 et 2019. Il ne s'agit pas d'une baisse réelle, mais d'un artefact de données. Pour satisfaire le livrable de l'histogramme (une variable numérique continue), nous avons utilisé la variable larrout (largeur de route). Les données sources pour cette variable sont massivement manquantes pour ces deux années, ce qui a entraîné la suppression de ces observations lors du nettoyage (dropna()).

2. Points chauds géographiques (Heatmap)
La carte de chaleur (density_mapbox) montre que la densité d'accidents est la plus forte dans les zones urbaines denses. Un point chaud particulièrement visible se situe sur Paris intra-muros, ainsi que dans les autres grandes métropoles (Lyon, Marseille, Bordeaux).

3. Analyse de la largeur de route (Histogramme)
L'histogramme (variable larrout) montre une distribution claire : la grande majorité des accidents se produit sur des routes d'une largeur "standard" (entre 3 et 7 mètres), ce qui correspond aux routes départementales, communales ou aux rues urbaines.

4. Gravité et Luminosité (Treemaps)
L'analyse des proportions (via les Treemaps) révèle deux faits majeurs :

Gravité : La très grande majorité des accidents n'entraîne heureusement que des "Blessés Légers". Les "Tués" (environ 1-2%) et "Blessés Graves" (environ 15-20%) représentent une part minoritaire mais très sérieuse des incidents.

Luminosité : Contrairement à une idée reçue, la majorité écrasante des accidents a lieu en "Plein jour", ce qui est logiquement corrélé au fait que la plupart des déplacements à vélo se font de jour.

© Copyright
Nous déclarons sur l’honneur que le code fourni a été produit par nous-mêmes, à l’exception des lignes ci-dessous :

L'utilisation du fichier external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] est une pratique standard issue de la documentation officielle de Dash pour l'utilisation de la grille CSS (lignes/colonnes).

Le token Mapbox (pk.eyJ1...) est le token public et gratuit fourni par Plotly dans sa documentation officielle pour permettre l'affichage des fonds de carte (density_mapbox).

Toute ligne non déclarée ci-dessus est réputée être produite par les auteurs du projet.