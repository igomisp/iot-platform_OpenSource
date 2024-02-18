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

# Inicializar la lista de children con las filas de id, type y location
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
        id="service_name",
        children=[
            dbc.Col(html.Div("service_name"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(dbc.Input(id="service_name-input", placeholder="service001")),
        ],
        align="center",
    ),
    dbc.Row(
        id="api_key",
        children=[
            dbc.Col(html.Div("api_key"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(
                dbc.Input(id="api_key-input", placeholder="4jggokgpepnvsb2uv4s40d59ov")
            ),
        ],
        align="center",
    ),
    dbc.Row(
        id="type_service",
        children=[
            dbc.Col(html.Div("type"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(
                dbc.Input(
                    id="type_service-input", placeholder="Device, Station, Sensor..."
                )
            ),
        ],
        align="center",
    ),
]


def layout():
    return [
        html.P("MQTT / CREATE SERVICE"),
        dbc.Container(
            id="container_create-service",
            children=entity_structure,
        ),
        dbc.Row(
            dbc.Button(
                id="add-attribute-service", children="Add attribute", color="primary"
            )
        ),
        dbc.Row(
            dbc.Button(id="create-service", children="Create service", color="success")
        ),
        dbc.Row(dbc.Input(id="status-code_create-service", disabled=True)),
    ]


@callback(
    Output("container_create-service", "children"),
    Input("add-attribute-service", "n_clicks"),
    State("container_create-service", "children"),
)
def add_attribute(n_clicks, children):
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


@callback(
    Output("status-code_create-service", "value"),
    Input("create-service", "n_clicks"),
    State("container_create-service", "children"),
)
def create_service(n_clicks, children):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # TODO: Handle service_name to use it as a identifier
        service_name = children[1]["props"]["children"][2]["props"]["children"][
            "props"
        ]["value"]

        api_key = children[2]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        type = children[3]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        json_dict = {
            "services": [
                {
                    "apikey": api_key,
                    "cbroker": f"http://{ORION_HOST}:{ORION_PORT}",
                    "entity_type": type,
                    "resource": "",
                    # TODO: check if it works with standard attributes.
                    # Therefore, we don't need to create the sensor because with the
                    # first measurement through the topic /<api-key>/<device-id>/attrs,
                    # the sensor will be created with device-id as entity_name, do we?
                    # But uri format for entity_name won't be fulfilled if the device_id
                    # on the IoT sensor is not set correctly
                    "attributes":
                    # Iterate over the children and add the attributes
                    [
                        {
                            "object_id": children[i]["props"]["children"][2]["props"][
                                "children"
                            ]["props"]["value"],
                            "name": children[i + 1]["props"]["children"][2]["props"][
                                "children"
                            ]["props"]["value"],
                            "type": children[i + 2]["props"]["children"][2]["props"][
                                "children"
                            ]["props"]["value"],
                        }
                        for i in range(4, len(children), 1)
                    ],
                }
            ]
        }

        newHeaders = {
            "fiware-service": "openiot",
            "fiware-servicepath": "/",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(
            f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/services",
            data=json.dumps(json_dict),
            headers=newHeaders,
        )

        if str(response.status_code)[0] == "2":
            return "Service group created successfully"
        else:
            return response.json()["name"] + "/" + response.json()["message"]
