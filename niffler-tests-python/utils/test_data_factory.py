from datetime import datetime
from pathlib import Path

from faker import Faker
import json

fake = Faker()

class TestDataFactory:

    @staticmethod
    def generate_user_data(count=1):
        user_data = []

        for _ in range(count):
            user_data.append({
                'username': fake.user_name(),
                'password': fake.password()
            })

        return user_data

    @staticmethod
    def save_to_file(data, filename):
        Path("test_data").mkdir(exist_ok=True)

        filepath = Path("test_data") / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def generate_test_data(save_data=False):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        data = {
            'user_data': TestDataFactory.generate_user_data()
        }
        if save_data:
            TestDataFactory.save_to_file(data, filename=f'test_data_{timestamp}.json')

        return data