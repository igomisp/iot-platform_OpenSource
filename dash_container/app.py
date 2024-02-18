import os

import dash_auth
import dash_bootstrap_components as dbc

import dash
from dash import Dash, html

# Import DASH_USER and DASH_PASS from environment variables
USERS_DICT = {os.getenv("DASH_USER", "iot"): os.getenv("DASH_PASS", "platform")}

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.LUMEN],
    # suppress_callback_exceptions=True,
)

auth = dash_auth.BasicAuth(app, USERS_DICT)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

ORION_HOST = os.getenv("ORION_HOST", "localhost")
DASH_PORT = os.getenv("DASH_PORT", 1250)
ORION_EXT_PORT = os.getenv("ORION_EXT_PORT", 1026)


# the styles for the main content position it to the right of the sidebar and
# add some padding.


sidebar = html.Div(
    [
        html.H2("IoT platform", className="display-4", style={"textAlign": "center"}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("HOME", href="/", active="exact"),
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                dbc.NavLink(
                                    "ENTITY LIST", href="/entities", active="exact"
                                ),
                                dbc.NavLink(
                                    "CREATE ENTITY",
                                    href="/create-entity",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "UPDATE ENTITY",
                                    href="/update-entity",
                                    active="exact",
                                ),
                            ],
                            title="FIWARE ENTITIES",
                        ),
                        dbc.AccordionItem(
                            [
                                dbc.NavLink(
                                    "SERVICES LIST",
                                    href="/mqtt-services",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "MQTT DEVICES LIST",
                                    href="/mqtt-entities",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "CREATE T&H ESP32 DEVICE",
                                    href="/create-t-h-esp32",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "CREATE MQTT SERVICE",
                                    href="/create-mqtt-service-group",
                                    active="exact",
                                ),
                                dbc.NavLink(
                                    "CREATE MQTT DEVICE",
                                    href="/create-mqtt-device",
                                    active="exact",
                                ),
                            ],
                            title="MQTT ENTITIES",
                        ),
                        dbc.AccordionItem(
                            [
                                dbc.NavLink(
                                    "DATA", href="/entities-data", active="exact"
                                ),
                                dbc.NavLink(
                                    "GRAPH",
                                    href="/visualization",
                                    active="exact",
                                ),
                            ],
                            title="ANALYTICS",
                        ),
                    ],
                    start_collapsed=True,
                    flush=True,
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

dash.page_container.style = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 2rem",
}

app.layout = dbc.Container(
    [
        sidebar,
        dash.page_container,
    ],
)


if __name__ == "__main__":
    # Allow remote connections
    app.run_server(host="0.0.0.0", port=DASH_PORT, debug=True)
