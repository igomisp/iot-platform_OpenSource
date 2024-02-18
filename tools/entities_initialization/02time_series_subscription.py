import json
import os

import requests

ORION_HOST = os.getenv("ORION_HOST", "localhost")


# Create subscription for Thermostat devices
json_dict = {
    "description": "Notify QuantumLeap of all context changes",
    "subject": {"entities": [{"idPattern": "urn:ngsi-ld:Thermostat:*"}]},
    "notification": {
        "http": {"url": "http://quantumleap:8668/v2/notify"},
        "attrs": ["temperature"],
        "metadata": ["dateCreated", "dateModified"],
    },
    "throttling": 1,
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/subscriptions",
    data=json.dumps(json_dict),
    headers=newHeaders,
)
print("Status code: ", response.status_code)


# Create subscription for Station device
json_dict = {
    "description": "Notify QuantumLeap of all context changes",
    "subject": {"entities": [{"idPattern": "urn:ngsi-ld:Station:*"}]},
    "notification": {
        "http": {"url": "http://quantumleap:8668/v2/notify"},
        "attrs": ["temperature", "humidity", "dewPoint", "windSpeed"],
        "metadata": ["dateCreated", "dateModified"],
    },
    "throttling": 1,
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/subscriptions",
    data=json.dumps(json_dict),
    headers=newHeaders,
)
print("Status code: ", response.status_code)


# Create subscription for Sensor devices
json_dict = {
    "description": "Notify QuantumLeap of all context changes",
    "subject": {"entities": [{"idPattern": "urn:ngsi-ld:Sensor:*"}]},
    "notification": {
        "http": {"url": "http://quantumleap:8668/v2/notify"},
        "attrs": ["humidity", "temperature"],
        "metadata": ["dateCreated", "dateModified"],
    },
    "throttling": 1,
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/subscriptions",
    data=json.dumps(json_dict),
    headers=newHeaders,
)
print("Status code: ", response.status_code)

json_dict = {
    "description": "Notify QuantumLeap of all context changes",
    "subject": {"entities": [{"idPattern": "urn:ngsi-ld:Sensor:*"}]},
    "notification": {
        "http": {"url": "http://quantumleap:8668/v2/notify"},
        "attrs": ["temperature", "humidity"],
        "metadata": ["dateCreated", "dateModified"],
    },
    "throttling": 1,
}

newHeaders = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/",
    "Content-type": "application/json",
    "Accept": "application/json",
}
response = requests.post(
    "http://" + ORION_HOST + ":1026/v2/subscriptions",
    data=json.dumps(json_dict),
    headers=newHeaders,
)
print("Status code: ", response.status_code)
