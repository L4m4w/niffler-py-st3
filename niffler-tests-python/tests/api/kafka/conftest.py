import pytest

from clients.kafka_client import KafkaClient


@pytest.fixture(scope="session")
def kafka(envs):
    """Взаимодействие с Kafka"""
    with KafkaClient(envs) as k:
        yield k