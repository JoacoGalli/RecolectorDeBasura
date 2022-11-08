import paho.mqtt.client
import time

def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        topic = "/metricas/test/"
        result = client.publish(topic, msg)
  
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1

def on_connect(client, userdata, flags, rc):
    print("connected (%s)" % client._client_id)
    client.subscribe(topic="metricas/mqtt", qos=2)

def on_message(client, userdat, message):
    print("--------------------------")
    print("topic: %s" % message.topic)
    print("payload: %s" % message.payload)
    print("qos: %d" % message.qos)

def main():
    client = paho.mqtt.client.Client(client_id='joaco-tesis', clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host='127.0.0.1', port=1883)
    publish(client)
    client.loop_forever()

if __name__ == '__main__':
    main()
