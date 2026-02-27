import json
import pika

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "iot.events"

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def callback(ch, method, properties, body):
        event = json.loads(body.decode("utf-8"))
        print("✅ Worker received:", event)

        # ACK: marcamos como procesado
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Prefetch=1 (un mensaje a la vez por worker)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print("👷 Worker running. Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()