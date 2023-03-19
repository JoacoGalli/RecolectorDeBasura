import paho.mqtt.client as mqtt
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import NamedTuple

class SensorData(NamedTuple):
    tag: str
    measurement: str
    value: float

class InfluxDB_Client:
    def __init__(self):
        self.url = 'http://localhost:8086'
        self.token = 'recolector_de_basura'
        self.org = 'recolector'
        self.database = 'metricas'
        self.client = InfluxDBClient(url=self.url, token=self.token, debug=None, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    # def write_metric(self, measurement, value, tags=None):
    #     point = self.__create_point(measurement, value, tags)
    #     print(point)
    #     self.write_api.write(self.database, record=point)

    # def __create_point(self, measurement, value, tags=None):
    #     point = {}
    #     point["measurement"] = measurement
    #     point["fields"] = {"value": float(value)}
    #     if tags:
    #         point["tags"] = tags
    #     return point
    def send_sensor_data_to_influxdb(self, sensor_data):
        json_body ={
            'measurement': sensor_data.measurement,
            'tags': {
                'sensor': sensor_data.tag
            },
            'fields': {
                'value': sensor_data.value
            }
        }
        print(json_body)
        point = Point.from_dict(json_body, WritePrecision.NS)
        self.write_api.write("metricas", "recolector", point)
        print(f"escribi {point}")


class MQTTClient(InfluxDB_Client):
    def __init__(self):
        self.broker_url = 'localhost'
        self.broker_port = 1883
        self.client = mqtt.Client()
        self.influxdb_client = InfluxDB_Client()
        self.client.connect(self.broker_url, self.broker_port)

    def send_metric(self, topic, metric):
        self.client.publish(topic, metric)
    
    def parse_mqtt_message(self, topic, payload):
        msg = topic.split('/') # [measurement,tag] [metrica,buffer]
        print(msg)
        if msg:
            measurement = msg[0]
            tag = msg[1]
            return SensorData(tag, measurement, float(payload))
        else:
            return None
    
    def on_message(self, client, userdata, msg):
        print("entre para imprimir algo")
        sensor_data = self.parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
        if sensor_data is not None:
            self.influxdb_client.send_sensor_data_to_influxdb(sensor_data)

    def run_mqtt_client(self):
        self.client.on_message = self.on_message
        self.client.subscribe("metricas/#")
        self.client.loop_forever()
