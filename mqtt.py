import paho.mqtt.client as mqtt
import json
import time
import random
import jwt
import ssl
import datetime

DEVICE_ID='my-device'
PROJECT_ID='arctic-defender-275118'
CLOUD_REGION='europe-west1'
REGISTRY_ID='data-project'
PRIVATE_KEY_FILE='./rsa_private.pem'
ALGORITHM='RS256'
CA_CERTS='roots.pem'
MQTT_BRIDGE_HOSTNAME='mqtt.googleapis.com'
MQTT_BRIDGE_PORT=8883

def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            An MQTT generated from the given project_id and private key, which
            expires in 60 minutes. After 60 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client = mqtt.Client(
            client_id=('projects/{}/locations/{}/registries/{}/devices/{}'
                       .format(
                               project_id,
                               cloud_region,
                               registry_id,
                               device_id)))

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client

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

mqtt_topic = '/devices/{}/events'.format(DEVICE_ID)
google_client = get_client(
        PROJECT_ID, CLOUD_REGION, REGISTRY_ID, DEVICE_ID,
        PRIVATE_KEY_FILE, ALGORITHM, CA_CERTS,
        MQTT_BRIDGE_HOSTNAME, MQTT_BRIDGE_PORT)

google_client.loop_start()
while True:
    client.loop()
    light, night, daytime = getLight(light, night, daytime)
    temp = getTemp(temp)
    distance = getDistance(distance)
    now = datetime.datetime.now()

    dict.update({"temp": temp, "distance": distance, "light": light, "now": now})
    message = json.dumps(dict, default=str)
    client.publish("grupo_k/data", message)
    google_client.publish(mqtt_topic, message, qos=1)
    print(message)
    time.sleep(period)
    
    



