import json
import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path_template="/mqtt-service-details/<service_id>")

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


def update_table(service_id):
    store_data = get_mqtt_services()

    # Check if <service_id> is an id of any entity in the store
    entities = store_data
    entity_details = None
    if entities is not None:
        for entity in entities["services"]:
            if entity["_id"] == service_id:
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
                            (
                                html.Tr(
                                    [
                                        html.Td(attr),
                                        html.Td(
                                            html.Pre(
                                                json.dumps(
                                                    [
                                                        {
                                                            "object_id": item.get(
                                                                "object_id", ""
                                                            ),
                                                            "name": item.get(
                                                                "name", ""
                                                            ),
                                                            "type": item.get(
                                                                "type", ""
                                                            ),
                                                        }
                                                        for item in entity_details[attr]
                                                    ],
                                                    ensure_ascii=False,
                                                )
                                            )
                                        ),
                                    ]
                                )
                            )
                            if isinstance(entity_details[attr], list)
                            and all(
                                isinstance(item, dict) for item in entity_details[attr]
                            )
                            else (
                                html.Tr(
                                    [
                                        html.Td(attr),
                                        html.Td(
                                            html.Pre(
                                                json.dumps(
                                                    entity_details[attr],
                                                    ensure_ascii=False,
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


def layout(service_id=None):
    return (
        dbc.Container(
            [
                dcc.Location(id="url", refresh=False),
                dbc.Row(dbc.Col(html.H1(f"Details for MQTT Service ID: {service_id}"))),
                dbc.Row(
                    dbc.Table(
                        id="entity-details",
                        bordered=True,
                        color="secondary",
                        children=update_table(service_id),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            id="delete-mqtt-service",
                            children="Delete entity",
                            color="danger",
                        ),
                        width=2,
                    )
                ),
                dbc.Row(dbc.Input(id="status-code_delete_mqtt_service", disabled=True)),
            ]
        ),
    )


# Callback to delete entity
@callback(
    Output("status-code_delete_mqtt_service", "value"),
    Input("delete-mqtt-service", "n_clicks"),
    State("url", "pathname"),
)
def delete_mqtt_service(n_clicks, pathname):
    if n_clicks is None or pathname is None:
        raise PreventUpdate
    else:
        apikey = None
        # Get entity id
        service_id = pathname.split("/")[-1]
        # Get the apikey of the service
        store_data = get_mqtt_services()
        entities = store_data
        entity_details = None
        if entities is not None:
            for entity in entities["services"]:
                if entity["_id"] == service_id:
                    entity_details = entity
                    break
            if entity_details is not None:

                apikey = entity_details["apikey"]
                resource = entity_details["resource"]

        # Context broker delete entity query
        newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
        url = f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/services/?resource={resource}&apikey={apikey}"

        response = requests.delete(url, headers=newHeaders)

        if str(response.status_code)[0] == "2":
            mqtt_service_deletion = "MQTT service deleted successfully"
        else:
            mqtt_service_deletion = (
                response.json()["error"] + "/" + response.json()["description"]
            )

        return mqtt_service_deletion
