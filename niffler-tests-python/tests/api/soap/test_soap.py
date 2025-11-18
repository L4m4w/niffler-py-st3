from pathlib import Path

import pytest

from templates.read_templates import country_iso_code_xml, country_name_xml, xsd_response
from templates.utils import check_result_operation


class TestSoap:

    def test_country_name_service(self, soap_client):

        response = soap_client.session.post(url = '', data = country_name_xml('Germany'))

        print(response.content)

        xsd_response('CountryISOCodeResponse').validate(response.text)

        assert response.status_code == 200
        assert check_result_operation(response.text, 'DE')

    def test_country_iso_code_service(self, soap_client):

        response = soap_client.session.post(url = '', data = country_iso_code_xml('DE'))

        print(response.content)

        xsd_response('CountryNameResponse').validate(response.text)

        assert response.status_code == 200
        assert check_result_operation(response.text, 'Germany')