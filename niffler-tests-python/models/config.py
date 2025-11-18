from pydantic import BaseModel
from typing import Dict, Any

class Envs(BaseModel):
    frontend_url: str
    gateway_url: str
    register_url: str
    auth_url: str
    auth_secret: str
    spend_db_url: str
    userdata_db_url: str
    test_username: str
    test_password: str
    kafka_address: str

    def get_safe_dict_for_log(self) -> Dict[str, Any]:
        data = self.model_dump()
        sensitive_fields = ['test_password', 'test_username', 'spend_db_url', 'userdata_db_url', 'auth_secret']
        for field in sensitive_fields:
            if field in data and data[field]:
                data[field] = '*****'
        return data