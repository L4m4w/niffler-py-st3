import json
import logging
from json import JSONDecodeError

import allure
import curlify
from allure_commons.types import AttachmentType
from requests import Response
from jinja2 import Template, Environment, PackageLoader,select_autoescape


def allure_attach_request(function):
    def wrapper(*args, **kwargs):
        method, url = args[0], args[1]

        with allure.step(f"{method} {url}"):
            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)

            env = Environment(
                loader=PackageLoader(".../resources"),
                autoescape=select_autoescape()
            )
            template = env.get_template("http-request.tpl")

            with allure.step(f"{method} {url}"):

                response: Response = function(*args, **kwargs)
                curl = curlify.to_curl(response.request)

                prepare_render = {
                    "request": response.request,
                    "curl": curl,
                }

                logging.debug(curl)

                render = template.render(prepare_render)

                allure.attach(
                    body=render,
                    name=f"Request",
                    attachment_type=AttachmentType.HTML,
                    extension=".html"
                )


            try:
                _response = json.dumps(response.json(), indent=4).encode('utf8')
                prepare_render = {
                    "response": _response
                }

                logging.debug(_response)

                render = template.render(prepare_render)

                allure.attach(
                    body=render,
                    name=f"Response body {response.status_code}",
                    attachment_type=AttachmentType.HTML,
                    extension=".html"
                )

            except JSONDecodeError:
                _response = response.text.encode('utf8')
                prepare_render = {
                    "response": _response
                }

                logging.debug(_response)

                render = template.render(prepare_render)

                allure.attach(
                    body=render,
                    name=f"Response text {response.status_code}",
                    attachment_type=AttachmentType.HTML,
                    extension=".html"
                )

            # allure.attach(
            #     body=json.dumps(response.headers, indent=4).encode('utf8'),
            #     name=f"Response headers{response.status_code}",
            #     attachment_type=AttachmentType.JSON,
            #     extension='.json'
            # )
        return response
    return wrapper
