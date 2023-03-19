import threading
from mqtt_influx_class import MQTTClient, InfluxDB_Client

mqtt_client = MQTTClient()
influxdb_client = InfluxDB_Client()

# def on_message(client, userdata, message):
#     print("entre para imprimir algo")
#     topic = message.topic
#     payload = message.payload.decode("utf-8")
#     influxdb_client.write_metric(topic, payload)

# def run_mqtt_client():
#     mqtt_client.client.on_message = on_message
#     mqtt_client.client.subscribe("metricas/#")
#     mqtt_client.client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
mqtt_thread.start()
x = 0
while x<10:
    mqtt_client.send_metric("metricas/prueba", x)
    x+=1
