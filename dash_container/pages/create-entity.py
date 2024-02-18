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
QUANTUMLEAP_HOST = os.getenv("QUANTUMLEAP_HOST", "localhost")
QUANTUMLEAP_EXT_PORT = os.getenv("QUANTUMLEAP_EXT_PORT", "8668")
# ORION_HOST = "orion"


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
        id="id",
        children=[
            dbc.Col(html.Div("id"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(dbc.Input(id="id-input", placeholder="urn:ngsi-ld:<name>:<XXX>")),
        ],
        align="center",
    ),
    dbc.Row(
        id="type",
        children=[
            dbc.Col(html.Div("type"), width=2),
            dbc.Col(html.Div("Text"), width=2),
            dbc.Col(
                dbc.Input(id="type-input", placeholder="Device, Station, Sensor...")
            ),
        ],
        align="center",
    ),
    dbc.Row(
        id="location",
        children=[
            dbc.Col(html.Div("location"), width=2),
            dbc.Col(html.Div("geo:json"), width=2),
            dbc.Col(dbc.Input(id="location-input", placeholder="[lon, lat]")),
        ],
        align="center",
    ),
]


def layout():
    return [
        html.P("FIWARE / CREATE"),
        dbc.Container(
            id="container_create",
            children=entity_structure,
        ),
        dbc.Row(
            dbc.Button(id="add-attribute", children="Add attribute", color="primary")
        ),
        dbc.Row(
            dbc.Button(id="create-entity", children="Create entity", color="success")
        ),
        dbc.Row(dbc.Input(id="status-code_create", disabled=True)),
        dbc.Row(dbc.Input(id="status-code_create_subs", disabled=True)),
    ]


@callback(
    Output("container_create", "children"),
    Input("add-attribute", "n_clicks"),
    State("container_create", "children"),
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
                    dbc.Col(dbc.Input(id="new-attribute-value", placeholder="Value")),
                ],
                align="center",
            )
        )
        return children


@callback(
    Output("status-code_create", "value"),
    Output("status-code_create_subs", "value"),
    Input("create-entity", "n_clicks"),
    State("container_create", "children"),
)
def create_entity(n_clicks, children):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # Get the values of the inputs
        id_ = children[1]["props"]["children"][2]["props"]["children"]["props"]["value"]

        type_ = children[2]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        location_ = json.loads(
            children[3]["props"]["children"][2]["props"]["children"]["props"]["value"]
        )
        # Create the payload
        payload = {
            "id": id_,
            "type": type_,
            "location": {
                "type": "geo:json",
                "value": {"type": "Point", "coordinates": location_},
            },
        }
        # Iterate over the children and add the attributes
        for child in children[4:]:
            # key = child.children[0].children[0].value
            key = child["props"]["children"][0]["props"]["children"]["props"]["value"]
            # type_ = child.children[1].children[0].value
            type_ = child["props"]["children"][1]["props"]["children"]["props"]["value"]
            # value_ = child.children[2].children[0].value
            value_ = child["props"]["children"][2]["props"]["children"]["props"][
                "value"
            ]
            if type_ == "Number":
                value_ = float(value_)
            payload[key] = {"type": type_, "value": value_}
        # print(payload)

        newHeaders = {
            "fiware-service": "openiot",
            "fiware-servicepath": "/",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(
            "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities",
            data=json.dumps(payload),
            headers=newHeaders,
        )

        if response.status_code != 201:
            device_creation = (
                response.json()["error"] + "/" + response.json()["description"]
            )
            subscription_creation = "No subscription created"
        else:
            device_creation = "Device created successfully"

            # print([key for key, value in payload.items() if value["type"] == "Number"])
            attrs = []
            for key, value in payload.items():
                if (
                    isinstance(value, dict)
                    and "type" in value
                    and value["type"] == "Number"
                ):
                    attrs.append(key)

            # Create subscription for all attributes typed as Number
            json_dict = {
                "description": "Notify QuantumLeap of all context changes",
                "subject": {"entities": [{"idPattern": id_}]},
                "notification": {
                    # localhost does not work when using docker-compose. Not sure why
                    "http": {
                        "url": f"http://quantumleap:{QUANTUMLEAP_EXT_PORT}/v2/notify"
                    },
                    # Get a list of attributes with type Number
                    "attrs": attrs,
                    "metadata": ["dateCreated", "dateModified"],
                },
                "throttling": 1,
            }

            response2 = requests.post(
                "http://" + ORION_HOST + f":{ORION_PORT}/v2/subscriptions",
                data=json.dumps(json_dict),
                headers=newHeaders,
            )
            # print("Status code: ", response2.status_code)
            # print("Response: ", response2.text)

            if response2.status_code != 201:
                subscription_creation = (
                    response2.json()["error"] + "/" + response2.json()["description"]
                )
            else:
                subscription_creation = "Subscription created successfully"

        return device_creation, subscription_creation
