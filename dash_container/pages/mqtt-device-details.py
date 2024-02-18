import json
import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__, path_template="/mqtt-device-details/<device_id>")

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
IOTA_HOST = os.getenv("IOTA_HOST", "localhost")
IOTA_EXT_NORTH_PORT = os.getenv("IOTA_EXT_NORTH_PORT", "4041")


def get_mqtt_devices():
    # Context broker entities query
    newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
    url = f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/devices"
    response = requests.get(url, headers=newHeaders)
    response.encoding = "utf-8"
    return response.json()


def update_table(device_id):
    store_data = get_mqtt_devices()

    # Check if <device_id> is an id of any entity in the store
    entities = store_data
    entity_details = None
    if entities is not None:
        for entity in entities["devices"]:
            if entity["device_id"] == device_id:
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


def layout(device_id=None):
    return (
        dbc.Container(
            [
                dcc.Location(id="url", refresh=False),
                dbc.Row(dbc.Col(html.H1(f"Details for MQTT Device ID: {device_id}"))),
                dbc.Row(
                    dbc.Table(
                        id="entity-details",
                        bordered=True,
                        color="secondary",
                        children=update_table(device_id),
                    ),
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Button(
                            id="delete-mqtt-device",
                            children="Delete entity",
                            color="danger",
                        ),
                        width=2,
                    )
                ),
                dbc.Row(dbc.Input(id="status-code_delete_mqtt_device", disabled=True)),
            ]
        ),
    )


# Callback to delete entity
@callback(
    Output("status-code_delete_mqtt_device", "value"),
    Input("delete-mqtt-device", "n_clicks"),
    Input("url", "pathname"),
)
def delete_mqtt_device(n_clicks, pathname):
    if n_clicks is None or pathname is None:
        raise PreventUpdate
    else:
        # Get entity id
        device_id = pathname.split("/")[-1]

        # Context broker delete entity query
        newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
        url = f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/devices/{device_id}"
        # print("url", url)
        response = requests.delete(url, headers=newHeaders)

        if str(response.status_code)[0] == "2":
            return "Device deleted successfully"
        else:
            return response.json()["name"] + "/" + response.json()["message"]
