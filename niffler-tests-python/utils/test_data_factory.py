from datetime import datetime
from pathlib import Path

import logging
from typing import List, Dict, Any

from faker import Faker
import json

from models.user import GetUsers, UserData

logger = logging.getLogger(__name__)

fake = Faker()

class TestDataFactory:

    def __init__(self, locale: str = "en_US"):
        self.fake = Faker(locale)
        self.generated_data = []
        logger.info(f"Initialized TestDataFactory with locale: {locale}")

    def _log_generation(self, data_type: str, data: Any):
        """Логирование генерации данных"""
        logger.debug(f"Generated {data_type}: {data}")
        self.generated_data.append({"type": data_type, "data": data})

    def generate_username(self) -> str:
        username = self.fake.user_name()
        logger.debug(f"Generated username: {username}")
        return username

    def generate_password(self, length: int = 10) -> str:
        password = self.fake.password(length=length)
        logger.debug(f"Generated password: {'*' * len(password)}")
        return password

    def create_user_credentials_data(self, save_data=False) -> UserData:
        username = self.generate_username()
        password = self.generate_password()

        user_data = UserData(
            username=username,
            password=password
        )

        self._log_generation("user_data", user_data)
        logger.info(f"Created user data: {user_data}")

        if save_data:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            TestDataFactory.save_to_file(user_data, filename=f'test_data_{timestamp}.json')

        return user_data

    def create_multiple_users(self, count: int = 3) -> List[UserData]:
        users = [self.create_user_credentials_data() for _ in range(count)]
        logger.info(f"Generated {count} users")
        return users

    @staticmethod
    def save_to_file(data, filename):
        Path("test_data").mkdir(exist_ok=True)

        filepath = Path("test_data") / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_generation_stats(self) -> Dict[str, int]:
        """Статистика сгенерированных данных"""
        stats = {}
        for item in self.generated_data:
            stats[item['type']] = stats.get(item['type'], 0) + 1
        return stats

    @classmethod
    def with_locale(cls, locale: str):
        """Альтернативный конструктор с указанием локали"""
        return cls(locale)

    @staticmethod
    def generate_test_data(save_data=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        username = fake.user_name()
        password = fake.password()

        data = {
            'user_data': {username, password}
        }
        if save_data:
            TestDataFactory.save_to_file(data, filename=f'test_data_{timestamp}.json')

        return username, password