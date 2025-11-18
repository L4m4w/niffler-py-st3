import json
import logging
from typing import Sequence

import pytest
from confluent_kafka import TopicPartition
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic, Consumer, Producer
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
from utils.waiters import wait_until_timeout

class KafkaClient:
    """Класс для взаимодействия с кафкой"""

    def __init__(
            self,
            envs,
            client_id: str = 'tester',
            group_id: str = 'tester',

    ):
        self.server = envs.kafka_address
        self.admin = AdminClient(
            {"bootstrap.servers": f"localhost:9092"}
            # {"bootstrap.servers": f"{self.server}:9092"}
        )
        self.producer = Producer(
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
        self.consumer = Consumer(
            {
                "bootstrap.servers": f"localhost:9093",
                "group.id": group_id,
                "client.id": client_id,
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                "enable.ssl.certificate.verification": False
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.consumer.close()
        self.producer.flush()

    def list_topics_names(self, attempts: int = 5):
        """Вернуть список доступных топиков"""
        try:
            topics = self.admin.list_topics(timeout=attempts).topics
            return [topics.get(item).topic for item in topics]
        except RuntimeError:
            logging.error("no topics in kafka")

    @wait_until_timeout
    def consume_message(self, partitions, **kwargs):
        """Вернуть последнее после определенной позиции сообщение"""
        self.consumer.assign(partitions)
        try:
            message = self.consumer.poll(1.0)
            logging.debug(f'{message.value()}')
            return message.value()
        except AttributeError:
            pass

    def get_last_offset(self, topic: str = "", partition_id=0):
        """Вернуть последнюю позицию партиции"""
        partition = TopicPartition(topic, partition_id)
        try:
            low, high = self.consumer.get_watermark_offsets(partition, timeout=10)
            return high
        except Exception as err:
            logging.error("probably no such topic: %s: %s", topic, err)

    def log_msg_and_json(self, topic_partitions):
        msg = self.consume_message(topic_partitions, timeout=25)
        logging.info(msg)
        return msg

    def subscribe_listen_new_offsets(self, topic):
        self.consumer.subscribe([topic])
        p_ids = self.consumer.list_topics(topic).topics[topic].partitions.keys()
        partitions_offsets_event = {k: self.get_last_offset(topic, k) for k in p_ids}
        logging.info(f'{topic} offsets: {partitions_offsets_event}')
        topic_partitions = [TopicPartition(topic, k, v) for k, v in partitions_offsets_event.items()]
        return topic_partitions

    def send_message(self, topic, message):
        try:
            # ii = self.producer

            # if not self._check_kafka_connection():
            #     pytest.fail("Kafka is not available")

            self.producer.produce(topic,
                                  value=message,
                                  callback=self._delivery_callback)
            self.producer.flush(timeout=10)
            print("Message produced successfully")

        except KafkaException as e:
            pytest.fail(f"Failed to produce message: {e}")


    def _delivery_callback(self, err, msg):
        """Callback для отслеживания доставки"""
        if err:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def _check_kafka_connection(self):
        """Проверка доступности Kafka"""
        try:
            # Простая проверка через list_topics


            self.consumer.list_topics(timeout=5)
            # self.consumer.close()
            return True
        except:
            return False

    def basic_consume_loop(self, topics):


        try:
            # подписываемся на топик
            self.consumer.subscribe(topics)

            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None: continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                         (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    print(f"Received message: {msg.value().decode('utf-8')}")
        except KeyboardInterrupt:
            pass
        # finally:
        #     self.consumer.close()

