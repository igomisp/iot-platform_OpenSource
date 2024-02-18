import json
import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path_template="/entity-details/<entity_id>")

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


def update_table(entity_id):
    store_data = get_entities()

    # Check if <entity_id> is an id of any entity in the store
    entities = store_data
    entity_details = None
    if entities is not None:
        for entity in entities:
            if entity["id"] == entity_id:
                entity_details = entity
                break
        if entity_details is not None:
            table_header = [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Attribute"),
                            html.Th("Value"),
                        ]
                    )
                )
            ]

            table_body = [
                html.Tbody(
                    [
                        (
                            html.Tr(
                                [
                                    html.Td(attr),
                                    # print(type(entity_details[attr])),
                                    html.Td(
                                        html.Pre(
                                            json.dumps(
                                                entity_details[attr], ensure_ascii=False
                                            )
                                        )
                                    ),
                                ]
                            )
                            if isinstance(entity_details[attr], dict)
                            else html.Tr(
                                [
                                    html.Td(attr),
                                    html.Td(entity_details[attr]),
                                ],
                            )
                        )
                        for attr in entity_details
                    ]
                )
            ]

            return table_header + table_body
        else:
            # Return empty table
            return [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Attribute"),
                            html.Th("Value"),
                        ]
                    )
                ),
                html.Tbody(),
            ]

    else:
        # Return empty table
        return [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Attribute"),
                        html.Th("Value"),
                    ]
                )
            ),
            html.Tbody(),
        ]


def layout(entity_id=None):
    return (
        dbc.Container(
            [
                dcc.Location(id="url", refresh=False),
                dbc.Row(dbc.Col(html.H1(f"Details for FIWARE Entity ID: {entity_id}"))),
                dbc.Row(
                    dbc.Table(
                        id="entity-details",
                        bordered=True,
                        color="secondary",
                        children=update_table(entity_id),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            id="delete-entity",
                            children="Delete entity",
                            color="danger",
                        ),
                        width=2,
                    )
                ),
                dbc.Row(dbc.Input(id="status-code_delete", disabled=True)),
            ]
        ),
    )


# Callback to delete entity
@callback(
    Output("status-code_delete", "value"),
    Input("delete-entity", "n_clicks"),
    State("url", "pathname"),
)
def delete_entity(n_clicks, pathname):
    if n_clicks is None or pathname is None:
        raise PreventUpdate
    else:
        # Get entity id
        entity_id = pathname.split("/")[-1]
        # Context broker delete entity query
        newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
        url = "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities/" + entity_id
        response = requests.delete(url, headers=newHeaders)
        # print(response.text)

        if str(response.status_code)[0] == "2":
            entity_deletion = "Entity deleted successfully"
            # Delete associated subscriptions
            url = "http://" + ORION_HOST + f":{ORION_PORT}/v2/subscriptions"
            response = requests.get(url, headers=newHeaders)
            response.encoding = "utf-8"
            subscriptions = response.json()

            for subscription in subscriptions:
                if subscription["subject"]["entities"][0]["idPattern"] == entity_id:
                    url = (
                        "http://"
                        + ORION_HOST
                        + f":{ORION_PORT}/v2/subscriptions/"
                        + subscription["id"]
                    )
                    response = requests.delete(url, headers=newHeaders)
                    # print(response.status_code, response.text)

        else:
            entity_deletion = (
                response.json()["error"] + "/" + response.json()["description"]
            )

        return entity_deletion
