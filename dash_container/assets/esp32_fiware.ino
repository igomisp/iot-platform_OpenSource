/*
  This is a fork from Rui Santos' project  https://RandomNerdTutorials.com/esp32-mqtt-publish-dht11-dht22-arduino/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include "DHT.h"
#include <WiFi.h>

#include <AsyncMqttClient.h>

// WiFi credentials
const char WIFI_SSID[] = SECRET_SSID;
const char WIFI_PASSWORD[] = SECRET_PASS;

// Raspberry Pi Mosquitto MQTT Broker
const char MQTT_HOST[] = SECRET_MQTT_HOST;
const int MQTT_PORT = SECRET_MQTT_PORT;

// Broker credentials
const char MQTT_USER[] = SECRET_MQTT_USER;
const char MQTT_USER_PASS[] = SECRET_MQTT_USER_PASS;

// Topic
const char MQTT_TOPIC[] = CONFIG_MQTT_TOPIC;

// Digital pin connected to the DHT sensor
#define DHTPIN 4  

// Uncomment whatever DHT sensor type you're using
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
//#define DHTTYPE DHT21   // DHT 21 (AM2301)   

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE, 22);

// Variables to hold sensor readings and message
float temp;
float hum;
char msg[50];

AsyncMqttClient mqttClient;

unsigned long previousMillis = 0;   // Stores last time temperature was published
const long interval = CONFIG_INTERVAL;        // Interval at which to publish sensor readings

bool wifiConnected = false;
bool mqttConnected = false;

void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connectToMqtt() {
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();
}

void WiFiEvent(WiFiEvent_t event) {
  Serial.printf("[WiFi-event] event: %d\n", event);
  switch(event) {
    case SYSTEM_EVENT_STA_GOT_IP:
      Serial.println("WiFi connected");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());
      wifiConnected = true;
      connectToMqtt();
      break;
    case SYSTEM_EVENT_STA_DISCONNECTED:
      Serial.println("WiFi lost connection");
      wifiConnected = false;
      break;
  }
}

void onMqttConnect(bool sessionPresent) {
  Serial.println("Connected to MQTT.");
  mqttConnected = true;
  Serial.print("Session present: ");
  Serial.println(sessionPresent);
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  Serial.println("Disconnected from MQTT.");
  mqttConnected = false;
}

void onMqttPublish(uint16_t packetId) {
  Serial.print("Publish acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  // Disable Bluetooth
  btStop();
  Serial.println("Bluetooth disabled");

  dht.begin();

  WiFi.onEvent(WiFiEvent);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCredentials(MQTT_USER, MQTT_USER_PASS);

}

void loop() {
  unsigned long currentMillis = millis();
  // Every X number of seconds (interval = XX miliseconds) 
  // it publishes a new MQTT message
  if (currentMillis - previousMillis >= interval) {
    Serial.println("Time to publish!");
    // Save the last time a new reading was published
    previousMillis = currentMillis;
    Serial.println("Change WiFi mode and connect to WiFi!");
    WiFi.mode(WIFI_STA);
    connectToWifi();
    while (!(wifiConnected && mqttConnected)) {
      Serial.println("Not ready!");
      delay(250);
    }

    Serial.println("Read sensor!");
    // New DHT sensor readings
    hum = dht.readHumidity();
    // Read temperature as Celsius (the default)
    temp = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    //temp = dht.readTemperature(true);

    // Check if any reads failed and exit early (to try again).
    while (isnan(temp) || isnan(hum) || hum > 100 || hum <= 0) {
      Serial.println(F("Failed to read from DHT sensor!"));
      hum = dht.readHumidity();
      temp = dht.readTemperature();
    }     
    
    sprintf(msg, "t|%s#h|%s", String(temp), String(hum));
    
    // Publish an MQTT message on topic MQTT_TOPIC
    // mqttClient.publish(topic, qos, retain, payload)
    uint16_t packetIdPub1 = mqttClient.publish(MQTT_TOPIC, 1, false, String(msg).c_str());                            
    Serial.printf("Publishing on topic %s at QoS 1, packetId: %i\n", MQTT_TOPIC, packetIdPub1);
    Serial.printf("Message: %s \n", msg);
    
    delay(150);
    
    mqttClient.disconnect();
    Serial.println("Disconnecting WiFi!");
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    Serial.println("WiFi disconnected!");    
    
  }
}