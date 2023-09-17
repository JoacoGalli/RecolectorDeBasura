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
contenedores = {"0":5,"1":20,"2":30,"3":27,"4":90,"5":56,"6":77,"7":100}
posicion_cinta = 3
mqtt_client.send_metric("metricas/distribucion_pos", posicion_cinta)
mqtt_client.send_metric("metricas/distribucion_pos_cm", 33)

for x in range(8):
    topic = "metricas/tacho" + str(x) 
    mqtt_client.send_metric(topic, contenedores[str(x)])
mqtt_client.send_metric("metricas/motor_traslacion", 1)
mqtt_client.send_metric("metricas/motor_rotacion_cap", 1)
mqtt_client.send_metric("metricas/motor_rotacion_dist", 1)
mqtt_client.send_metric("metricas/motor_rotacion_cap_vel", 0.1)
mqtt_client.send_metric("metricas/motor_rotacion_dist_vel", 0.1)
for x in [10,29,49,69,80,100,80,85,70,55,22,0]:
    mqtt_client.send_metric("metricas/buffer", x)

mqtt_client.send_metric("metricas/codigo", 1)
