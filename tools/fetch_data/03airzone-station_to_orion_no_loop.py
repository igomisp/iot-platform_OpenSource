# %%
import datetime
import json
import os
import time

import requests
from get_raspberry_json import get_raspberry_json
from weather_station_injection import weather_station_fetch

ORION_HOST = os.getenv("ORION_HOST", "localhost")


def store_api_data_orion(devices, installation_id):
    get_raspberry_json()
    with open("current_tokens.json", "r") as f:
        keys = json.load(f)
        token = keys["token"]
        refresh_token = keys["refreshToken"]

    print("Token from file")

    for device_id in devices:
        URL = f"https://m.airzonecloud.com/api/v1/devices/{device_id}/status"
        headers = {"accept": "application/json", "authorization": f"Bearer {token}"}
        params = {"installation_id": installation_id}

        response = requests.get(URL, headers=headers, params=params)
        if response.status_code == 401:
            print("Error with request")
            get_raspberry_json()
            with open("current_tokens.json", "r") as f:
                keys = json.load(f)
                token = keys["token"]
                refresh_token = keys["refreshToken"]

            print("New token")
            print(token)
            print(refresh_token)

            headers = {"accept": "application/json", "authorization": f"Bearer {token}"}
            response = requests.get(URL, headers=headers, params=params)

        data = response.json()
        value = data["local_temp"]["celsius"]
        print(device_id)
        print(devices[device_id])
        print(value)

        current_time = datetime.datetime.now().isoformat()
        print(current_time)

        json_dict = {"temperature": {"type": "Number", "value": value}}

        orion_id = devices_orion[device_id]
        newHeaders = {
            "fiware-service": "openiot",
            "fiware-servicepath": "/",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        response = requests.post(
            "http://" + ORION_HOST + f":1026/v2/entities/{orion_id}/attrs",
            data=json.dumps(json_dict),
            headers=newHeaders,
        )
        # if we use requests.put (instead requests.post), attributes are replaced by the used at the request

        # success code - 204
        print(response)

        print(response.text)


def store_station_data():
    url = "http://150.214.57.165/meteo/Current_Vantage.htm"
    data = weather_station_fetch(url)

    json_dict = {}
    for k, v in data.items():
        if k == "Temperatura":
            json_dict["temperature"] = {"type": "Number", "value": float(v)}
        elif k == "Humedad":
            json_dict["humidity"] = {"type": "Number", "value": float(v)}
        elif k == "Punto de rocío":
            json_dict["dewPoint"] = {"type": "Number", "value": float(v)}
        else:
            json_dict["windSpeed"] = {"type": "Text", "value": v}
    newHeaders = {
        "fiware-service": "openiot",
        "fiware-servicepath": "/",
        "Content-type": "application/json",
        "Accept": "application/json",
    }
    response = requests.post(
        "http://" + ORION_HOST + ":1026/v2/entities/urn:ngsi-ld:Station:001/attrs",
        data=json.dumps(json_dict),
        headers=newHeaders,
    )
    print(response.status_code)


if __name__ == "__main__":
    installation_id = "60f9a49a91e52341716586a3"
    devices = {
        "619e4af8a43d67819d7d0277": "Salón",
        "619e4af8a43d67819d7d0278": "Dormitorio",
        "619e4af8a43d67819d7d0279": "Vestidor",
        "619e4af8a43d67819d7d027a": "Trastero",
    }

    devices_orion = {
        "619e4af8a43d67819d7d0277": "urn:ngsi-ld:Thermostat:001",
        "619e4af8a43d67819d7d0278": "urn:ngsi-ld:Thermostat:002",
        "619e4af8a43d67819d7d0279": "urn:ngsi-ld:Thermostat:003",
        "619e4af8a43d67819d7d027a": "urn:ngsi-ld:Thermostat:004",
    }


    try:
        store_api_data_orion(devices, installation_id)
        store_station_data()
    except Exception as e:
        print(datetime.datetime.now().isoformat())
        print(e)