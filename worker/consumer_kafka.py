import os, json, time, requests
from kafka import KafkaConsumer

SERVER = os.getenv("CLOUD_SERVER", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")
TOPIC = os.getenv("KAFKA_TOPIC", "smartpole.events")
BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092").split(",")

def main():
    headers = {"x-api-key": API_KEY} if API_KEY else {}
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BROKERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="smartpole-consumers",
    )
    print(f"[kafka] consuming {TOPIC} from {BROKERS}")
    for msg in consumer:
        try:
            r = requests.post(f"{SERVER}/ingest/message", json=msg.value, headers=headers, timeout=5)
            print("[kafka] ->", r.status_code)
        except Exception as e:
            print("[kafka] error:", e); time.sleep(1)

if __name__ == "__main__": main()
