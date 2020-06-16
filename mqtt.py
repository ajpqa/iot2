import paho.mqtt.client as mqtt
import json
import time
import random

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

night_length = 8
period = 1

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
time.sleep(1)

light = 0
night = night_length
daytime = "am"
distance = 330
temp = 25

dict = {}

def getLight(light, night, daytime):
    if light == 0:
        if night > 0:
            night -= 1
        else:
            night = night_length
            light += 10
    elif daytime == "am":
        light += 10
        if light == 470:
            daytime = "pm"
    else:
        light -= 10
        if light == 0:
            daytime = "am"
    return light, night, daytime

def getTemp(temp):
    coin = random.random()
    if temp > 40:
        return temp - temp*random.random()
    elif temp < 10:
        return temp + temp*random.random()
    elif coin > 0.5:
        return temp + temp*random.random()*0.1
    else:
        return temp - temp*random.random()*0.1

def getDistance(distance):
    coin = random.random()
    if coin < 0.85:
        if distance == 330:
            return distance
        else:
            return distance*random.random()
    else:
        if distance == 330:
            return distance*random.random()
        else:
            return 330

while True:
    client.loop()
    light, night, daytime = getLight(light, night, daytime)
    temp = getTemp(temp)
    distance = getDistance(distance)

    dict.update({"temp": temp, "distance": distance, "light": light})
    message = json.dumps(dict)
    client.publish("grupo_k/data", message)
    print(message)
    time.sleep(period)
    
    



