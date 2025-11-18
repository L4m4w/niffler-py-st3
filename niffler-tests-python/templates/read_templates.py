import xmlschema
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from xmlschema import XMLSchema11

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

def country_iso_code_xml(country_iso_code: str) -> str:
    template = env.get_template('/templates/xml/country_iso_code.xml')
    return template.render({'country_iso_code': country_iso_code})

def country_name_xml(country_name: str) -> str:
    template = env.get_template('/templates/xml/country_name.xml')
    return template.render({'country_name': country_name})


def xsd_response(operation: str = 'CountryISOCodeResponse') -> XMLSchema11:
    envelope_xsd = env.get_template('./templates/xsd/envelope.xsd')
    country_iso_code_xsd_response = envelope_xsd.render(
        {'operation_xsd': f'{operation}.xsd', 'operation': f'{operation}'}
    )

    with open('./templates/xsd/temp.xsd', 'w') as f:
        f.write(country_iso_code_xsd_response)

    return xmlschema.XMLSchema11('./templates/xsd/temp.xsd')
