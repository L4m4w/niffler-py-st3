from confluent_kafka import Consumer, KafkaException, KafkaError, Producer
import sys
import logging

def create_consumer(config):
    consumer = Consumer(config)

    def basic_consume_loop(topics):
        try:
            # подписываемся на топик
            consumer.subscribe(topics)

            # send_message('users', 'hello')

            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    print(f"Received message: {msg.value().decode('utf-8')}")
                    consumer.close()

        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    return basic_consume_loop

def send_message(topic, message):
        try:
            producer = Producer(
                {
                    "bootstrap.servers": f"localhost:9092",
                    "message.max.bytes": 10000000,  # 10MB max
                    "compression.type": "gzip",  # сжатие
                    "batch.size": 16384,  # размер батча
                    "linger.ms": 5,
                    # "value.serializer": "utf-8"
                }
                # {"bootstrap.servers": f"{self.server}:9092"}
            )

            producer.produce(topic,
                                  value=message)
            producer.flush(timeout=10)
            print("Message produced successfully")

        except KafkaException as e:
            print(f"Failed to produce message: {e}")

def main():
    kafka_config = {
        'bootstrap.servers': 'localhost:9093',
        'group.id': 'userdata',
        'client.id': 'tester',
        'auto.offset.reset': 'earliest'
    }


    consumer_loop = create_consumer(kafka_config)
    consumer_loop(['users',])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()