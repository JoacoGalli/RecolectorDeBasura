#!/usr/bin/python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
from typing import NamedTuple
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_ADDRESS = 'http://localhost:8086'
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = '123456789'
INFLUXDB_DATABASE = 'metricas'

influxdb_client = InfluxDBClient(url=INFLUXDB_ADDRESS, token='recolector_de_basura', debug=None, org='recolector')
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

class SensorData(NamedTuple):
    tag: str
    measurement: str
    value: float

class MyMQTTClass(mqtt.Client):

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_connect_fail(self, mqttc, obj):
        print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        print(f'{msg.payload=}')
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        sensor_data = self._parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
        if sensor_data is not None:
            self._send_sensor_data_to_influxdb(sensor_data)

    def on_publish(self, mqttc, obj, msg):
        # self.on_message(mqttc,)
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)
    
    def _parse_mqtt_message(self, topic, payload):
        msg = topic.split('/') # [measurement,tag] [metrica,buffer]
        print(msg)
        if msg:
            measurement = msg[0]
            tag = msg[1]
            return SensorData(tag, measurement, float(payload))
        else:
            return None
    
    def _send_sensor_data_to_influxdb(self, sensor_data):
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
        write_api.write("metricas", "recolector", point)
        print(f"escribi {point}")

    def run(self):
        self.connect("localhost", 1883, 60)
        self.subscribe("metricas/#", 0)

        rc = 0
        while rc == 0:
            rc = self.loop()
        return rc


# If you want to use a specific client id, use
# mqttc = MyMQTTClass("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = MyMQTTClass()
rc = mqttc.run()

# print("rc: "+str(rc))