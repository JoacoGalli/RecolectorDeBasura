/*
 Basic ESP8266 MQTT example
 This sketch demonstrates the capabilities of the pubsub library in combination
 with the ESP8266 board/library.
 It connects to an MQTT server then:
  - publishes "hello world" to the topic "outTopic" every two seconds
  - subscribes to the topic "inTopic", printing out any messages
    it receives. NB - it assumes the received payloads are strings not binary
  - If the first character of the topic "inTopic" is an 1, switch ON the ESP Led,
    else switch it off
 It will reconnect to the server if the connection is lost using a blocking
 reconnect function. See the 'mqtt_reconnect_nonblocking' example for how to
 achieve the same result without blocking the main loop.
 To install the ESP8266 board, (using Arduino 1.6.4+):
  - Add the following 3rd party board manager under "File -> Preferences -> Additional Boards Manager URLs":
       http://arduino.esp8266.com/stable/package_esp8266com_index.json
  - Open the "Tools -> Board -> Board Manager" and click install for the ESP8266"
  - Select your ESP8266 in "Tools -> Board"
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>

// Update these with values suitable for your network.

const char* ssid = "TheScharnEmpire2.4GHz";
const char* password = "riquelme10";
const char* mqtt_server = "192.168.0.19";

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (100)     
char msg[MSG_BUFFER_SIZE];
int value = 0;
String arduinoData;

void setup() {
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  Serial.begin(9600);
  Serial.flush();
  delay(1000);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {   // loops until connected.
    delay(500);
  }
  client.setServer(mqtt_server, 1883);
  //client.setCallback(callback);

  Serial.flush();
}

void loop() {
  if (!client.connected()) {
      while (!client.connected()) {               // Loop until we're reconnected 
        client.connect("GER-ESP8266Client-");     // it's irrelevant
      }
  }
  client.loop();

  if(Serial.available()){
    char sensorType;
    String sensorData;
    
    arduinoData = Serial.readString();
    sensorType = arduinoData.charAt(0);  
    sensorData = arduinoData.substring(2);
    
    snprintf (msg, MSG_BUFFER_SIZE, "%s", sensorData);

    switch (sensorType) {
      case 'A':
        client.publish("SensorTypeA", msg);
        break;
      case 'B':
        client.publish("SensorTypeB", msg);
        break;
      default:
        client.publish("ERROR", msg);
        break;
    }
  }
  Serial.flush();
  delay(10);
}
