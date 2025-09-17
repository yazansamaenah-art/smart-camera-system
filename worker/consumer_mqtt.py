import os, json, requests
import paho.mqtt.client as mqtt

SERVER = os.getenv("CLOUD_SERVER", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")
BROKER = os.getenv("MQTT_BROKER", "localhost")
TOPIC = os.getenv("MQTT_TOPIC", "smartpole/events")

headers = {"x-api-key": API_KEY} if API_KEY else {}

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        r = requests.post(f"{SERVER}/ingest/message", json=payload, headers=headers, timeout=5)
        print("[mqtt] ->", r.status_code)
    except Exception as e:
        print("[mqtt] error:", e)

def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC, qos=1)
    client.loop_forever()

if __name__ == "__main__": main()
