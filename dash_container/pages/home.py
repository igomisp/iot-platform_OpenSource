# %%

import os

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests

import dash
from dash import dcc, html

dash.register_page(__name__, path="/")

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
# ORION_HOST = "orion"

"""
# Move to the right part of the sidebar
dash.page_container.style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
"""


def update_map_figure(store_data):
    entities = store_data
    # Entities is a list of dicts
    # Get the dicts which have location as a key
    if entities is None:
        entities_with_location = []
    else:
        entities_with_location = [
            entity for entity in entities if "location" in entity.keys()
        ]

    # Get the location values and the id in a list
    data = [
        [
            entity["id"],
            entity["location"]["value"]["coordinates"][0],
            entity["location"]["value"]["coordinates"][1],
            entity["temperature"]["value"],
        ]
        for entity in entities_with_location
    ]

    df = pd.DataFrame(data, columns=["id", "long", "lat", "temp"])

    mapbox_token = os.getenv("MAPBOX_TOKEN")

    if mapbox_token is None:
        raise ValueError("No mapbox token found")

    px.set_mapbox_access_token(mapbox_token)

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="long",
        hover_name="id",
        zoom=11,
        color="temp",
        height=800,
    )
    fig.update_traces(cluster=dict(enabled=True))

    return fig


def get_entities():
    # Context broker entities query
    newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
    url = "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities"
    response = requests.get(url, headers=newHeaders)
    response.encoding = "utf-8"
    return response.json()


def layout():
    entities = get_entities()

    return dbc.Container(
        [
            html.P("Home page"),
            dcc.Graph(id="map", figure=update_map_figure(entities)),
        ],
    )


# %%
