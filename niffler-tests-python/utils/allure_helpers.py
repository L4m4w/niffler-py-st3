import json
import logging
from json import JSONDecodeError

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response



def allure_attach_request(function):
    def wrapper(*args, **kwargs):
        method, url = args[0], args[1]

        with allure.step(f"{method} {url}"):
            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)
            logging.debug(curl)
            allure.attach(
                body=curl,
                name='Request curl',
                attachment_type=AttachmentType.TEXT,
                extension='.txt'
            )
            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode('utf8'),
                    name=f"Response body {response.status_code}",
                    attachment_type=AttachmentType.JSON,
                    extension='.json'
                )
                logging.debug(response.text)
            except JSONDecodeError:
                allure.attach(
                    body=response.text.encode('utf8'),
                    name=f"Response text {response.status_code}",
                    attachment_type=AttachmentType.TEXT,
                    extension='.txt'
                )

            # allure.attach(
            #     body=json.dumps(response.headers, indent=4).encode('utf8'),
            #     name=f"Response headers{response.status_code}",
            #     attachment_type=AttachmentType.JSON,
            #     extension='.json'
            # )
        return response
    return wrapper
