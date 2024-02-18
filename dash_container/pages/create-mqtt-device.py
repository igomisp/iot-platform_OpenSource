import json
import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
IOTA_HOST = os.getenv("IOTA_HOST", "localhost")
IOTA_EXT_NORTH_PORT = os.getenv("IOTA_EXT_NORTH_PORT", "4041")


"""
"devices": [
   {
     "device_id":   "motion001",
     "entity_name": "urn:ngsi-ld:Motion:001",
     "entity_type": "Motion",
     "protocol":    "PDI-IoTA-UltraLight",
     "transport":   "MQTT",
     "timezone":    "Europe/Berlin",
     "attributes": [
       { "object_id": "c", "name": "count", "type": "Integer" }
     ],
     "static_attributes": [
       { "name":"refStore", "type": "Relationship", "value": "urn:ngsi-ld:Store:001"}
     ]
   }
 ]
"""
entity_structure = [
    dbc.Row(
        id="header",
        children=[
            dbc.Col(
                dbc.Badge("Attribute", color="primary", className="me-1"),
                width=2,
            ),
            dbc.Col(
                dbc.Badge("Type", color="primary", className="me-1"),
                width=2,
            ),
            dbc.Col(
                dbc.Badge("Value", color="primary", className="me-1"),
                width=2,
            ),
        ],
    ),
    dbc.Row(
        id="device_id",
        children=[
            dbc.Col(html.Div("device_id"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(dbc.Input(id="device_id-input", placeholder="device_id")),
        ],
        align="center",
    ),
    dbc.Row(
        id="api_key",
        children=[
            dbc.Col(html.Div("entity_name"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(
                dbc.Input(id="api_key-input", placeholder="urn:ngsi-ld:<entity_name>")
            ),
        ],
        align="center",
    ),
    dbc.Row(
        id="type_service",
        children=[
            dbc.Col(html.Div("entity_type"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(
                dbc.Input(
                    id="type_service-input", placeholder="Device, Station, Sensor..."
                )
            ),
        ],
        align="center",
    ),
    dbc.Row(
        id="location",
        children=[
            dbc.Col(html.Div("location"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(dbc.Input(id="location-input", placeholder="[lon,lat]")),
        ],
        align="center",
    ),
]


def layout():
    return [
        html.P("MQTT / CREATE MQTT DEVICE"),
        dbc.Container(
            id="container_create-mqtt-device",
            children=entity_structure,
        ),
        dbc.Row(
            dbc.Button(
                id="add-mqtt-attribute", children="Add mqtt attribute", color="primary"
            )
        ),
        dbc.Row(
            dbc.Button(
                id="create-mqtt-device", children="Create MQTT device", color="success"
            )
        ),
        dbc.Row(dbc.Input(id="status-code_create-mqtt-device", disabled=True)),
    ]


@callback(
    Output("container_create-mqtt-device", "children"),
    Input("add-mqtt-attribute", "n_clicks"),
    State("container_create-mqtt-device", "children"),
)
def add_attribute_mqtt_device(n_clicks, children):
    if n_clicks is None:
        raise PreventUpdate
    else:
        children.append(
            dbc.Row(
                id="new-attribute",
                children=[
                    dbc.Col(
                        dbc.Input(
                            id="new-attribute-key",
                            placeholder="Attribute",
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="new-attribute-type",
                            options=[
                                {"label": "Text", "value": "Text"},
                                {"label": "Number", "value": "Number"},
                            ],
                            placeholder="Type",
                        ),
                        # dbc.Input(id="new-attribute-type", placeholder="Type"),
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Input(
                            id="new-attribute-value", placeholder="mqtt attribute key"
                        )
                    ),
                ],
                align="center",
            )
        )
        return children


# TODO: Addapt create_mqtt_device to sensor attributes
@callback(
    Output("status-code_create-mqtt-device", "value"),
    Input("create-mqtt-device", "n_clicks"),
    State("container_create-mqtt-device", "children"),
)
def create_mqtt_device(n_clicks, children):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # TODO: Handle service_name to use it as a identifier
        device_id = children[1]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        entity_name = children[2]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        entity_type = children[3]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        json_dict = {
            "devices": [
                {
                    "device_id": device_id,
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "timezone": "Europe/Madrid",
                    "attributes": [],
                    "protocol": "PDI-IoTA-UltraLight",
                    "transport": "MQTT",
                }
            ]
        }

        # If "value" is a key in the dictionary, create location
        if "value" in children[4]["props"]["children"][2]["props"]["children"]["props"]:
            location = json.loads(
                children[4]["props"]["children"][2]["props"]["children"]["props"][
                    "value"
                ]
            )
            json_dict["devices"][0]["static_attributes"] = [
                {
                    "name": "location",
                    "type": "geo:json",
                    "value": {"type": "Point", "coordinates": location},
                }
            ]
        # Iterate over the children and add the attributes
        # TODO: Probably Type is always Text...
        for child in children[5:]:
            # key = child.children[0].children[0].value
            name_ = child["props"]["children"][0]["props"]["children"]["props"]["value"]
            # type_ = child.children[1].children[0].value
            type_ = child["props"]["children"][1]["props"]["children"]["props"]["value"]
            # value_ = child.children[2].children[0].value
            object_id_ = child["props"]["children"][2]["props"]["children"]["props"][
                "value"
            ]

            json_dict["devices"][0]["attributes"].append(
                {"object_id": object_id_, "name": name_, "type": type_}
            )

        # print("json_dict", json_dict)

        newHeaders = {
            "fiware-service": "openiot",
            "fiware-servicepath": "/",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(
            f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/devices",
            data=json.dumps(json_dict),
            headers=newHeaders,
        )

        if str(response.status_code)[0] == "2":
            return "MQTT device created successfully"
        else:
            return response.json()["error"] + "/" + response.json()["description"]
