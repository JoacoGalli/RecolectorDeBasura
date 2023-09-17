#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge
This script receives MQTT data and saves those to InfluxDB.
"""

from cmath import inf
import re
from turtle import position
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb_client import WritePrecision, InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUXDB_ADDRESS = 'http://localhost:8086'
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = '123456789'
INFLUXDB_DATABASE = 'metricas'

MQTT_ADDRESS = 'localhost'
MQTT_TOPIC = 'metricas/#'  # [room]/[temperature|humidity|light|status]


influxdb_client = InfluxDBClient(url=INFLUXDB_ADDRESS, token='recolector_de_basura', debug=None, org='recolector')
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

class SensorData(NamedTuple):
    tag: str
    measurement: str
    value: float


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    if sensor_data is not None:
        _send_sensor_data_to_influxdb(sensor_data)


def _parse_mqtt_message(topic, payload):
    msg = topic.split('/') # [measurement,tag] [metrica,buffer]
    print(msg)
    if msg:
        measurement = msg[0]
        tag = msg[1]
        return SensorData(tag, measurement, float(payload))
    else:
        return None


def _send_sensor_data_to_influxdb(sensor_data):
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


""" def _init_influxdb_database():
    databases = influxdb_client.get_list_database()
    if len(list(filter(lambda x: x['name'] == INFLUXDB_DATABASE, databases))) == 0:
        influxdb_client.create_database(INFLUXDB_DATABASE)
    influxdb_client.switch_database(INFLUXDB_DATABASE)
 """

def main():
    #_init_influxdb_database()

    mqtt_client = mqtt.Client()
    #mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()
