import json

import allure

from faker import Faker

from clients.auth_client import AuthClient
from models.user import UserName


@allure.epic("[KAFKA][niffler-auth]: Паблишинг сообщений в кафку")
@allure.suite("[KAFKA][niffler-auth]: Паблишинг сообщений в кафку")
class TestAuthRegistrationKafkaTest:

        @allure.title("KAFKA: Сообщение с пользователем публикуется в Kafka после успешной регистрации")
        @allure.tag("KAFKA")
        def test_message_should_be_produced_to_kafka_after_successful_registration(self, register_client, kafka):
                username = Faker().user_name()
                password = Faker().password(special_chars=False)

                # kafka.send_message('test_topic', 'Hello!')

                # kafka.basic_consume_loop(['test_topic'])

                # topic_partitions = kafka.subscribe_listen_new_offsets("users")

                # result = auth_client.register(username, password)

                topic_partitions = kafka.subscribe_listen_new_offsets("__consumer_offsets")

                result = register_client.register(username, password)
                # assert result.status_code == 200

                # assert result.status_code == 400

                event = kafka.log_msg_and_json(topic_partitions)

                li = json.loads(event.hex())
                # li = json.loads(event.decode('utf8'))
                pi = 1

                with allure.step("Check that message from kafka exist"):
                        assert event != '' and event != b''

                with allure.step("Check message content"):
                        UserName.model_validate(json.loads(event.decode('utf8')))
                        assert json.loads(event.decode('utf8'))['username'] == username


import socket
from confluent_kafka import Consumer

def test_check_kafka_connection():
    servers = ["localhost:9092", "kafka:9092", "127.0.0.1:9092"]

    for server in servers:
        print(f"Testing connection to {server}...")
        try:
            # Проверка TCP подключения
            host, port = server.split(":")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            sock.close()

            if result == 0:
                print(f"✓ TCP connection to {server} successful")

                # Проверка Kafka protocol
                consumer = Consumer({
                    'bootstrap.servers': server,
                    'group.id': 'test',
                    'session.timeout.ms': 5000
                })
                topics = consumer.list_topics(timeout=5)
                consumer.close()
                print(f"✓ Kafka protocol working on {server}")
                print(f"  Available topics: {list(topics.topics.keys())}")
                return server
            else:
                print(f"✗ TCP connection to {server} failed")

        except Exception as e:
            print(f"✗ Kafka test failed: {e}")

    return None


import socket
from confluent_kafka import Consumer


def test_connections():
    servers = [
        ("localhost:9092", "Standard port"),
        ("localhost:9093", "Your configured port"),
        ("kafka:9092", "Docker internal"),
    ]

    for server, description in servers:
        print(f"\nTesting {description} ({server})...")

        # TCP проверка
        host, port = server.split(":")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, int(port)))
            sock.close()

            if result == 0:
                print(f"  ✅ TCP connection successful")

                # Kafka protocol проверка
                try:
                    consumer = Consumer({
                        'bootstrap.servers': server,
                        'group.id': 'test',
                        'session.timeout.ms': 5000
                    })
                    topics = consumer.list_topics(timeout=5)
                    consumer.close()
                    print(f"  ✅ Kafka protocol working")
                    print(f"  📋 Topics: {list(topics.topics.keys())[:3]}...")
                    return server
                except Exception as e:
                    print(f"  ❌ Kafka protocol failed: {e}")
            else:
                print(f"  ❌ TCP connection failed")

        except Exception as e:
            print(f"  ❌ Connection test failed: {e}")

    return None


if __name__ == "__main__":
    working = test_connections()
    if working:
        print(f"\n🎯 Use this server: {working}")
    else:
        print(f"\n❌ No working Kafka connection found")

