import json
import os

import requests

ORION_HOST = os.getenv("ORION_HOST", "localhost")

json_dict = {
    "id": "urn:ngsi-ld:Thermostat:001",
    "type": "Device",
    "temperature": {
        "type": "Number",
        "value": None,
        "metadata": {
            "origin": {"value": "AIRZONE_CLOUD", "type": "Text"},
            "id_az": {"value": "619e4af8a43d67819d7d0277", "type": "Text"},
        },
    },
    "location": {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [-4.486664, 36.71853]},
    },
    "zone": {"type": "Text", "value": "Salón"},
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/entities",
    data=json.dumps(json_dict),
    headers=newHeaders,
)

print("Status code: ", response.status_code)
print(response.text)

json_dict = {
    "id": "urn:ngsi-ld:Thermostat:002",
    "type": "Device",
    "temperature": {
        "type": "Number",
        "value": None,
        "metadata": {
            "origin": {"value": "AIRZONE_CLOUD", "type": "Text"},
            "id_az": {"value": "619e4af8a43d67819d7d0278", "type": "Text"},
        },
    },
    "location": {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [-4.486656, 36.718501]},
    },
    "zone": {"type": "Text", "value": "Habitación"},
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/entities",
    data=json.dumps(json_dict),
    headers=newHeaders,
)

print("Status code: ", response.status_code)
print(response.text)

json_dict = {
    "id": "urn:ngsi-ld:Thermostat:003",
    "type": "Device",
    "temperature": {
        "type": "Number",
        "value": None,
        "metadata": {
            "origin": {"value": "AIRZONE_CLOUD", "type": "Text"},
            "id_az": {"value": "619e4af8a43d67819d7d0279", "type": "Text"},
        },
    },
    "location": {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [-4.486709, 36.718502]},
    },
    "zone": {"type": "Text", "value": "Vestidor"},
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/entities",
    data=json.dumps(json_dict),
    headers=newHeaders,
)

print("Status code: ", response.status_code)
print(response.text)

json_dict = {
    "id": "urn:ngsi-ld:Thermostat:004",
    "type": "Device",
    "temperature": {
        "type": "Number",
        "value": None,
        "metadata": {
            "origin": {"value": "AIRZONE_CLOUD", "type": "Text"},
            "id_az": {"value": "619e4af8a43d67819d7d027a", "type": "Text"},
        },
    },
    "location": {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [-4.486693, 36.718475]},
    },
    "zone": {"type": "Text", "value": "Trastero"},
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/entities",
    data=json.dumps(json_dict),
    headers=newHeaders,
)

print("Status code: ", response.status_code)
print(response.text)

json_dict = {
    "id": "urn:ngsi-ld:Station:001",
    "type": "Station",
    "name": {
        "type": "Text",
        "value": "Estación meteorológica Teatinos UMA",
        "metadata": {
            "id_meteoclimatic": {"value": "ESAND2900000029071B", "type": "Text"}
        },
    },
    "url": {"type": "URL", "value": "http://150.214.57.165/meteo/Current_Vantage.htm"},
    "temperature": {
        "type": "Number",
        "value": None,
        "metadata": {"origin": {"value": "WEB", "type": "Text"}},
    },
    "humidity": {
        "type": "Number",
        "value": None,
        "metadata": {"origin": {"value": "WEB", "type": "Text"}},
    },
    "dewPoint": {
        "type": "Number",
        "value": None,
        "metadata": {"origin": {"value": "WEB", "type": "Text"}},
    },
    "location": {
        "type": "geo:json",
        "value": {"type": "Point", "coordinates": [-4.47806, 36.71528]},
    },
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/entities",
    data=json.dumps(json_dict),
    headers=newHeaders,
)

print("Status code: ", response.status_code)
print(response.text)
