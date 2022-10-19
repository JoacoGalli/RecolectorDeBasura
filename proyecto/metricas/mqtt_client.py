import paho.mqtt.client
import time

class Mqtt_client():
    def __init__(self):
        self.client = paho.mqtt.client.Client(client_id='joaco', clean_session=False)
        self.client.connect(host='127.0.0.1', port=1883)
        #self.client.loop_forever()

    def publish(self, topic, data):
            result = self.client.publish(topic, data)

mqtt_client = Mqtt_client()
mqtt_client.publish('Pruebas')
