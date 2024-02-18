import json
import os
from time import sleep

import dash_bootstrap_components as dbc
import requests

import dash
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

dash.register_page(__name__)

ORION_HOST = os.getenv("ORION_HOST", "localhost")
ORION_PORT = os.getenv("ORION_PORT", "1026")
IOTA_HOST = os.getenv("IOTA_HOST", "localhost")
IOTA_EXT_NORTH_PORT = os.getenv("IOTA_EXT_NORTH_PORT", "4041")


def get_iot_services():
    newHeaders = {
        "fiware-service": "openiot",
        "fiware-servicepath": "/",
        "Content-type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(
        f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/services",
        headers=newHeaders,
    )
    # print("Status code: ", response.status_code)
    response.encoding = "utf-8"
    return response.json()


# Python script para modificar variables en un archivo Arduino local
def arduino_code_create_t_h_esp32(
    wifi_name,
    wifi_pass,
    mqtt_host,
    mqtt_port,
    mqtt_user,
    mqtt_pass,
    api_key,
    device_id,
    interval,
):
    pass
    # Ruta al archivo Arduino local
    arduino_code_path = "./assets/esp32_fiware.ino"

    # Leer el contenido del archivo Arduino
    with open(arduino_code_path, "r") as file:
        arduino_code = file.read()

    # Reemplazar variables de Arduino con variables de Python
    arduino_code = arduino_code.replace(
        "const char WIFI_SSID[] = SECRET_SSID;",
        f'const char WIFI_SSID[] = "{wifi_name}";',
    )
    arduino_code = arduino_code.replace(
        "const char WIFI_PASSWORD[] = SECRET_PASS;",
        f'const char WIFI_PASSWORD[] = "{wifi_pass}";',
    )
    arduino_code = arduino_code.replace(
        "const char MQTT_HOST[] = SECRET_MQTT_HOST;",
        f'const char MQTT_HOST[] = "{mqtt_host}";',
    )
    arduino_code = arduino_code.replace(
        "const int MQTT_PORT = SECRET_MQTT_PORT;", f"const int MQTT_PORT = {mqtt_port};"
    )
    arduino_code = arduino_code.replace(
        "const char MQTT_USER[] = SECRET_MQTT_USER;",
        f'const char MQTT_USER[] = "{mqtt_user}";',
    )
    arduino_code = arduino_code.replace(
        "const char MQTT_USER_PASS[] = SECRET_MQTT_USER_PASS;",
        f'const char MQTT_USER_PASS[] = "{mqtt_pass}";',
    )
    arduino_code = arduino_code.replace(
        "const char MQTT_TOPIC[] = CONFIG_MQTT_TOPIC;",
        f'const char MQTT_TOPIC[] = "/{api_key}/{device_id}/attrs";',
    )
    arduino_code = arduino_code.replace(
        "const long interval = CONFIG_INTERVAL;",
        f"const long interval = {int(interval)*1000};",
    )

    # Guardar el código Arduino modificado en un nuevo archivo
    with open(f"./assets/{api_key}_{device_id}.ino", "w") as file:
        file.write(arduino_code)

    print(
        "Arduino code created: ",
        f'"{api_key}_{device_id}".ino',
    )


def layout():
    services = get_iot_services()["services"]

    dropdown_options = [
        {"label": service["apikey"], "value": service["apikey"]} for service in services
    ]
    dropdown_options.append({"label": "New service", "value": "New service"})

    # print(dropdown_options)
    entity_structure = [
        # header
        # 0
        dbc.Row(
            id="header_esp32",
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
        # api_key_esp32
        # 1
        dbc.Row(
            id="api_key_esp32",
            children=[
                dbc.Col(html.Div("api_key"), width=2),
                dbc.Col(
                    dbc.Select(
                        id="api_key-existing",
                        options=dropdown_options,
                        placeholder="Service",
                    ),
                    width=2,
                ),
                dbc.Col(
                    dbc.Input(
                        id="input-group-dropdown-input",
                        placeholder="api_key",
                        disabled=True,
                    ),
                ),
            ],
            align="center",
        ),
        # device_id_esp32
        # 2
        dbc.Row(
            id="device_id_esp32",
            children=[
                dbc.Col(html.Div("device_id"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="device_id-input", placeholder="device_id")),
            ],
            align="center",
        ),
        # wifi_name
        # 3
        dbc.Row(
            id="wifi_name_esp32",
            children=[
                dbc.Col(html.Div("WiFi SSID"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="wifi_name-input", placeholder="wifi_name")),
            ],
            align="center",
        ),
        # wifi_pass
        # 4
        dbc.Row(
            id="wifi_pass_esp32",
            children=[
                dbc.Col(html.Div("WiFi PASS"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="wifi_pass-input", placeholder="wifi_pass")),
            ],
            align="center",
        ),
        # mqtt_host
        # 5
        dbc.Row(
            id="mqtt_host_esp32",
            children=[
                dbc.Col(html.Div("MQTT Host"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="mqtt_host-input", placeholder="mqtt_host")),
            ],
            align="center",
        ),
        # mqtt_port
        # 6
        dbc.Row(
            id="mqtt_port_esp32",
            children=[
                dbc.Col(html.Div("MQTT Port"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="mqtt_port-input", placeholder="mqtt_port")),
            ],
            align="center",
        ),
        # mqtt_user
        # 7
        dbc.Row(
            id="mqtt_user_esp32",
            children=[
                dbc.Col(html.Div("MQTT User"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="mqtt_user-input", placeholder="mqtt_user")),
            ],
            align="center",
        ),
        # mqtt_pass
        # 8
        dbc.Row(
            id="mqtt_pass_esp32",
            children=[
                dbc.Col(html.Div("MQTT Pass"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(dbc.Input(id="mqtt_pass_esp32-input", placeholder="mqtt_pass")),
            ],
            align="center",
        ),
        # entity_name_esp32
        # 9
        dbc.Row(
            id="entity_name_esp32",
            children=[
                dbc.Col(html.Div("entity_name"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(
                    dbc.Input(
                        id="entity_name_esp32-attribute",
                        placeholder="device_id",
                    )
                ),
            ],
            align="center",
        ),
        # entity_type_esp32
        # 10
        dbc.Row(
            id="type_esp32",
            children=[
                dbc.Col(html.Div("entity_type"), width=2),
                dbc.Col(html.Div("Text"), width=2),
                dbc.Col(
                    dbc.Input(
                        id="type_esp32-attribute",
                        value="ESP32_TH_SENSOR",
                        disabled=True,
                    )
                ),
            ],
            align="center",
        ),
        # temperature_esp32
        # 11
        dbc.Row(
            id="temperature_esp32",
            children=[
                dbc.Col(html.Div("temperature"), width=2),
                dbc.Col(html.Div("Number"), width=2),
                dbc.Col(
                    dbc.Input(
                        id="temperature_esp32-attribute",
                        value="t",
                        disabled=True,
                    )
                ),
            ],
            align="center",
        ),
        # humidity_esp32
        # 12
        dbc.Row(
            id="humidity_esp32",
            children=[
                dbc.Col(html.Div("humidity"), width=2),
                dbc.Col(html.Div("Number"), width=2),
                dbc.Col(
                    dbc.Input(
                        id="humidity_esp32-attribute",
                        value="h",
                        disabled=True,
                    )
                ),
            ],
            align="center",
        ),
        # interval_esp32
        # 13
        dbc.Row(
            id="interval_esp32",
            children=[
                dbc.Col(html.Div("interval"), width=2),
                dbc.Col(html.Div("Number"), width=2),
                dbc.Col(
                    dbc.Input(
                        id="interval_esp32-attribute",
                        placeholder="measurement interval in seconds",
                    )
                ),
            ],
            align="center",
        ),
    ]

    return [
        html.P("MQTT / CREATE ESP32 T&H"),
        dbc.Container(
            id="container_create-t-h-esp32-device",
            children=entity_structure,
        ),
        dbc.Row(
            dbc.Button(
                id="create-t-h-esp32-device",
                children="Create T&H ESP32 device",
                color="success",
            )
        ),
        dbc.Row(dbc.Input(id="status-code_create-t-h-esp32-device", disabled=True)),
        dbc.Button("Download Arduino code", id="download-arduino-code-btn"),
        dcc.Download(id="download-arduino-code"),
    ]


@callback(
    Output("download-arduino-code", "data"),
    Input("download-arduino-code-btn", "n_clicks"),
    State("input-group-dropdown-input", "value"),
    State("device_id-input", "value"),
    prevent_initial_call=True,
)
def func(n_clicks, api_key, device_id):
    if n_clicks is None:
        raise PreventUpdate

    with open(f"./assets/{api_key}_{device_id}.ino", "r") as file:
        file = file.read()
    return dict(content=file, filename=f"{api_key}_{device_id}.ino")


# A callback that updates the api_key-input value when the dropdown is changed
@callback(
    Output("input-group-dropdown-input", "value"),
    Output("input-group-dropdown-input", "disabled"),
    Input("api_key-existing", "value"),
)
def update_input_group_dropdown(api_key):
    if api_key is None:
        raise PreventUpdate
    else:
        if api_key == "New service":
            disabled = False
            return "", disabled
        return api_key, True


@callback(
    Output("status-code_create-t-h-esp32-device", "value"),
    Input("create-t-h-esp32-device", "n_clicks"),
    State("container_create-t-h-esp32-device", "children"),
    State("api_key-existing", "value"),
)
def create_mqtt_device(n_clicks, children, api_key_type):
    if n_clicks is None:
        raise PreventUpdate
    else:
        api_key = children[1]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        device_id = children[2]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]
        # TODO: Create the arduino code
        wifi_name = children[3]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        wifi_pass = children[4]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        mqtt_host = children[5]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        mqtt_port = children[6]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        mqtt_user = children[7]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        mqtt_pass = children[8]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        entity_name = children[9]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        entity_type = children[10]["props"]["children"][2]["props"]["children"][
            "props"
        ]["value"]

        temperature = children[11]["props"]["children"][2]["props"]["children"][
            "props"
        ]["value"]

        humidity = children[12]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        interval = children[13]["props"]["children"][2]["props"]["children"]["props"][
            "value"
        ]

        if api_key == "":
            return "No api_key provided"

        json_dict = {
            "devices": [
                {
                    "device_id": device_id,
                    "entity_name": entity_name,
                    "entity_type": entity_type,
                    "timezone": "Europe/Madrid",
                    "attributes": [
                        {
                            "object_id": temperature,
                            "name": "temperature",
                            "type": "Number",
                        },
                        {"object_id": humidity, "name": "humidity", "type": "Number"},
                    ],
                    "protocol": "PDI-IoTA-UltraLight",
                    "transport": "MQTT",
                }
            ]
        }

        arduino_code_create_t_h_esp32(
            wifi_name,
            wifi_pass,
            mqtt_host,
            mqtt_port,
            mqtt_user,
            mqtt_pass,
            api_key,
            device_id,
            interval,
        )

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
            esp32_th_device_creation = "ESP32 T&H device created successfully"

            # Create MQTT service
            if api_key_type == "New service":
                json_dict = {
                    "services": [
                        {
                            "apikey": api_key,
                            "cbroker": f"http://{ORION_HOST}:{ORION_PORT}",
                            "entity_type": entity_type,
                            "resource": "",
                        }
                    ]
                }

                response2 = requests.post(
                    f"http://{IOTA_HOST}:{IOTA_EXT_NORTH_PORT}/iot/services",
                    data=json.dumps(json_dict),
                    headers=newHeaders,
                )

                if str(response2.status_code)[0] == "2":
                    esp32_th_device_creation = (
                        esp32_th_device_creation
                        + " and MQTT service created successfully"
                    )
                else:
                    esp32_th_device_creation = (
                        esp32_th_device_creation
                        + " and "
                        + response2.json()["name"]
                        + "/"
                        + response2.json()["message"]
                    )

        else:
            print(response.json())
            esp32_th_device_creation = (
                response.json()["name"] + "/" + response.json()["message"]
            )
            sleep(5)

        return esp32_th_device_creation
