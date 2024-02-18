import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import dcc, html

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
# ORION_HOST = "orion"


def get_entities():
    # Context broker entities query
    newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
    url = "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities"
    response = requests.get(url, headers=newHeaders)
    response.encoding = "utf-8"
    return response.json()


dash.register_page(__name__)

# Move to the right part of the sidebar
"""dash.page_container.style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}"""

# Refresh layout when the page is loaded


def layout():
    entities = get_entities()

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("id"),
                    html.Th("type"),
                ]
            )
        )
    ]

    if len(entities) > 0:
        table_body = [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                dcc.Link(
                                    entity["id"],
                                    href=f"/entity-details/{entity['id']}",
                                    style={
                                        "color": "blue",
                                        "textDecoration": "underline",
                                    },
                                )
                            ),
                            html.Td(entity["type"]),
                        ]
                    )
                    for entity in entities
                ]
            )
        ]

        table = dbc.Table(
            table_header + table_body, bordered=True, striped=True, color="light"
        )
    else:
        table = html.P("No entities found")

    return html.Div(
        [
            dcc.Location(id="url-entities", refresh=True),
            html.P("FIWARE / LIST"),
            table,
        ]
    )
