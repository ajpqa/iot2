#include <SoftwareSerial.h>
//#include <ESP8266Wifi.h> //easy management of Wifi over ESP8266 but libraray not available in Tinkercad
//#include <PubSubClient.h> //MQTT library, not available in Tinkercad
#include <ArduinoJson.h> //to convert
#define DEBUG true

int photoPin = 0;
int tempPin = 1;
int distancePin = 2;
int readPhoto;
float readTemp;
float readDistance;

const char* ssid = "MASTER";
const char* password = "malagaiot";

const char* mqtt_server = "iot.ac.uma.es";
const char* mqtt_user = "master";
const char* mqtt_pass = "malagaiot";

SoftwareSerial esp8266(7,6);

void setup()
{
  pinMode(tempPin, INPUT);
  pinMode(photoPin, INPUT);
  pinMode(distancePin, INPUT);
  Serial.begin(9600);
  
  //connect to the wifi using the library (not possible in Tinkercad)
  //setup_wifi();
  //time_wifi = millis();
  //printf("WiFi connected after %d ms\n", time_wifi);
  
  //instead try to connect using SoftwareSerial
  esp8266.begin(115200);
  sendData("AT+RST\r\n",1000,DEBUG); // reset module
  sendData("AT+CWMODE=1\r\n",1000,DEBUG); // configure as Wireless Station mode
  sendData("AT+CWJAP=\"SSID\",\"PASSWORD\"\r\n", 6000, DEBUG); //Put Your SSID and password if activate as Station mode else comment down the line
  sendData("AT+CIFSR\r\n",2000,DEBUG); // get ip address
  
  
  
  //connect to the mqtt server (not possible in Tinkercad)
  /*
  client.setServer(mqtt_server, 1883);
  snprintf(mqtt_cliente, 50, "ESP_%d", ESP.getChipId());
  Serial.print("Mi ID es ");
  Serial.println(mqtt_cliente);*/
}

long readUltrasonicDistance(int triggerPin, int echoPin)
{
  pinMode(triggerPin, OUTPUT);  // Clear the trigger
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  // Sets the trigger pin to HIGH state for 10 microseconds
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  pinMode(echoPin, INPUT);
  // Reads the echo pin, and returns the sound wave travel time in microseconds
  return pulseIn(echoPin, HIGH);
}

//function to send command to ESP8266 
void sendData(String command, const int timeout, boolean debug)
{
    esp8266.print(command); // send the read character to the esp8266
    long int time = millis();

    while( (time+timeout) > millis())
    {
      while(esp8266.available())
      {
        // The esp has data so display its output to the serial window 
        Serial.write(esp8266.read());
      }  
    }
}

void loop()
{
  //connect to MQTT server and start MQTT loop
  //if (!client.connected()) {
  //  reconnect();
  //}
  //client.loop();
  
  readPhoto = analogRead(photoPin); //471 is max
  
  readTemp = analogRead(tempPin);
  readTemp = readTemp*5000/1024;
  readTemp = readTemp-500;
  readTemp = readTemp/10; //converted to degree Celsius
  
  readDistance = 0.01723 * readUltrasonicDistance(2, 3);
  Serial.print("Distance: ");
  Serial.print(readDistance);
  Serial.print("\n");
  
  if (readPhoto < 170) {
  	Serial.println("night");
  }else{
    Serial.println("day");
  }
  Serial.print("Temp: ");
  Serial.println(readTemp);
  
  
  //convert measured data to json
  StaticJsonBuffer<300> JSONbuffer;
  JsonObject& JSONencoder = JSONbuffer.createObject();
  JSONencoder["temp"] = readTemp;
  JSONencoder["distance"] = readDistance;
  JSONencoder["light"] = readPhoto;
  
  char JSONmessageBuffer[100];
  JSONencoder.printTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  Serial.println(JSONmessageBuffer);
  Serial.print("\n--------------\n\n");
    
  //publish json to grupo_k/data
  //client.publish("grupo_k/data", JSONmessageBuffer);
    
   
  
  delay(1000); 
}

//setting up the Wifi using the ESP8266Wifi library
/*
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }



  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

}

//called when receiving data from the subsribed topic
void callback(const char* topic, byte* payload, unsigned int length) {

  char *topic_json = (char*) malloc(length + 1); // + 1 because we need to put the \0 at the end

  for(unsigned int i=0;i<=length;i++){
    if(i == length)
      topic_json[i] = '\0';
    else
      topic_json[i] = (char) payload[i];
  }
  
  Serial.printf("%s\n", topic_json);

  //parse the JSON and turn on the corresponding LED

  DynamicJsonDocument topic_json_document(length*4);

  DeserializationError error = deserializeJson(topic_json_document, topic_json);

  //Handle error and show debug messages
  if(error) {
    Serial.printf("ERROR: Invalid JSON input from topic: <%s>\n", topic);
    Serial.println(error.c_str());
    return;
  }
  
  //possible actions for received data can be added here
  //at the moment not needed
  
  free(topic_json); // we read the string, we can now free the memory
  topic_json = NULL;
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(mqtt_cliente, mqtt_user, mqtt_pass, "grupo_k/data", 0, 1, "Disconnected")) {
      Serial.println("connected");
      // Once connected, publish an announcement...

      client.publish("grupo_k/data", "Connected!", true);

      //subscribe to topics:

      if(client.subscribe("grupo_k/arduino")) {
        Serial.println("Subscribed succesfully!");
      } else {
        Serial.println("Error subscribing!");
      }

      client.setCallback(callback);

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
*/
