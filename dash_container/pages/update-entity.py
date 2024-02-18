import json
import os

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")


def get_entities():
    # Context broker entities query
    newHeaders = {"fiware-service": "openiot", "fiware-servicepath": "/"}
    url = "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities"
    response = requests.get(url, headers=newHeaders)
    response.encoding = "utf-8"
    return response.json()


def layout():
    entities = get_entities()
    return [
        html.P("FIWARE / UPDATE"),
        dbc.Row(
            dcc.Dropdown(
                id="dropdown-test",
                options=[
                    {"label": entity["id"], "value": entity["id"]}
                    for entity in entities
                ],
            ),
        ),
        dbc.Container(
            id="container",
        ),
        # Agregar la fila de botones al final
        dbc.Row(
            id="buttons",
            children=[
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Enable/Disable modification",
                            id="enable-mod",
                            color="primary",
                            className="me-1",
                        ),
                        dbc.Button(
                            "Send modification",
                            id="send-mod",
                            color="success",
                            className="me-1",
                        ),
                    ]
                ),
            ],
        ),
        dbc.Row(dbc.Input(id="status-code_update", disabled=True)),
    ]


# TODO: status-code_update is triggering a provisional error when creating entity
# Output in app.py and update-entity.py
@callback(
    Output("status-code_update", "value"),
    Input("send-mod", "n_clicks"),
    State("dropdown-test", "value"),
    State("container", "children"),
)
def send_mod(n_clicks, entity_id, children):
    if n_clicks is None or entity_id is None or len(entity_id) == 0:

        raise PreventUpdate
    else:
        json_dict = {}
        # Children is a list of dbc.Row
        for row in children:
            if row["props"]["id"] not in ["header", "id", "type"]:

                # Add to json_dict the key and value is a dict with type and value
                if row["props"]["id"] == "location":
                    json_dict[row["props"]["id"]] = dict(
                        type=row["props"]["children"][1]["props"]["children"]["props"][
                            "children"
                        ],
                        value=dict(
                            type="Point",
                            coordinates=json.loads(
                                row["props"]["children"][2]["props"]["children"][
                                    "props"
                                ]["value"]
                            ),
                        ),
                    )

                else:
                    if (
                        row["props"]["children"][1]["props"]["children"]["props"][
                            "children"
                        ]
                        == "Number"
                    ):
                        json_dict[row["props"]["id"]] = dict(
                            type=row["props"]["children"][1]["props"]["children"][
                                "props"
                            ]["children"],
                            value=float(
                                row["props"]["children"][2]["props"]["children"][
                                    "props"
                                ]["value"]
                            ),
                        )
                    else:
                        json_dict[row["props"]["id"]] = dict(
                            type=row["props"]["children"][1]["props"]["children"][
                                "props"
                            ]["children"],
                            value=row["props"]["children"][2]["props"]["children"][
                                "props"
                            ]["value"],
                        )

        newHeaders = {
            "fiware-service": "openiot",
            "fiware-servicepath": "/",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(
            "http://" + ORION_HOST + f":{ORION_PORT}/v2/entities/{entity_id}/attrs",
            data=json.dumps(json_dict),
            headers=newHeaders,
        )

        if str(response.status_code)[0] == "2":
            return "Entity updated successfully"
        else:
            return response.json()["error"] + "/" + response.json()["description"]


@callback(
    Output("dropdown-test", "options"),
    Input("status-code_update", "value"),
)
def dropdown_update(status_code_update):
    entities = get_entities()
    return [{"label": entity["id"], "value": entity["id"]} for entity in entities]


@callback(
    Output("container", "children"),
    Input("dropdown-test", "value"),
    Input("enable-mod", "n_clicks"),
)
def show_data_in_table(entity_id, n_clicks):
    store_data = get_entities()
    if entity_id is None or store_data is None or len(store_data) == 0:
        raise PreventUpdate
    else:
        if n_clicks is None or n_clicks % 2 == 0:
            disabled = True
        else:
            disabled = False
        # Select object from store_data which id is entity_id
        for entity in store_data:
            if entity["id"] == entity_id:
                data = entity
                break

        # Inicializar la lista de children con las filas de id, type y location
        children = [
            dbc.Row(
                id="header",
                children=[
                    dbc.Col(
                        dbc.Badge("Attribute", color="primary", className="me-1"),
                        width=1,
                    ),
                    dbc.Col(
                        dbc.Badge("Type", color="primary", className="me-1"),
                        width=1,
                    ),
                    dbc.Col(
                        dbc.Badge("Value", color="primary", className="me-1"),
                        width=1,
                    ),
                ],
            ),
            dbc.Row(
                id="id",
                children=[
                    dbc.Col(html.Div("id"), width=1),
                    dbc.Col(html.Div(), width=1),
                    dbc.Col(dbc.Input(value=data["id"], disabled=True)),
                ],
                align="center",
            ),
            dbc.Row(
                id="type",
                children=[
                    dbc.Col(html.Div("type"), width=1),
                    dbc.Col(html.Div(), width=1),
                    dbc.Col(dbc.Input(value=data["type"], disabled=True)),
                ],
                align="center",
            ),
        ]

        # Iterar sobre las claves del objeto data y agregar filas dinámicas
        for key, value in data.items():
            if key not in ["id", "type"]:
                if key == "location":
                    value_ = json.dumps(value["value"]["coordinates"])
                else:
                    value_ = value["value"]
                children.append(
                    dbc.Row(
                        id=key,
                        children=[
                            dbc.Col(html.Div(key), width=1),
                            dbc.Col(html.Div(value["type"]), width=1),
                            dbc.Col(
                                dbc.Input(
                                    value=value_,
                                    id=f"{key}-input",
                                    disabled=disabled,
                                )
                            ),
                        ],
                        align="center",
                    )
                )

        return children
