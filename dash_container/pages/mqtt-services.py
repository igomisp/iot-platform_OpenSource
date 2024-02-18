import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import dcc, html

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
IOTA_HOST = os.getenv("IOTA_HOST", "localhost")
IOTA_EXT_NORTH_PORT = os.getenv("IOTA_EXT_NORTH_PORT", "4041")


def get_mqtt_services():
    # Context broker entities query
    newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
    url = f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/services"
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

    entities = get_mqtt_services()
    # print("entities", entities)

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("id"),
                    html.Th("api_key"),
                    html.Th("type"),
                ]
            )
        )
    ]

    if entities["count"] > 0:
        table_body = [
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                dcc.Link(
                                    entity["_id"],
                                    href=f"/mqtt-service-details/{entity['_id']}",
                                    style={
                                        "color": "blue",
                                        "textDecoration": "underline",
                                    },
                                )
                            ),
                            html.Td(entity["apikey"]),
                            html.Td(entity["entity_type"]),
                        ]
                    )
                    for entity in entities["services"]
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
            html.P("MQTT / SERVICES LIST"),
            table,
        ]
    )
