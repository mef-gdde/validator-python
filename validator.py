import os
from flask import Flask, request, jsonify
from lxml import etree

app = Flask(__name__)

class XSDResolver(etree.Resolver):
    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path

    def resolve(self, url, pubid, context):
        path = os.path.join(self.base_path, url)
        if os.path.isfile(path):
            return self.resolve_filename(path, context)
        else:
            return None

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

parser = etree.XMLParser()
parser.resolvers.add(XSDResolver('validation-schema/maindoc/'))
xsd_file_path = '/Users/phaney/dev/e-invoice/python-validator/validation-schema/maindoc/UBL-Invoice-2.1.xsd'
xsd_content = read_file(xsd_file_path)
# Parse the XSD schema
xsd_root = etree.XML(xsd_content.encode('utf-8'), parser)

def validate_xml(xml_content):
    try:
       
        xsd_doc = etree.XMLSchema(xsd_root)

        # Parse the XML content
        xml_doc = etree.fromstring(xml_content.encode('utf-8'))

        # Validate the XML content against the XSD schema
        is_valid = xsd_doc.validate(xml_doc)
        if is_valid:
            return {"valid": True, "errors": []}
        else:
            errors = [error.message for error in xsd_doc.error_log]
            return {"valid": False, "errors": errors}
    except etree.XMLSyntaxError as e:
        return {"valid": False, "errors": [f"XML Syntax Error: {e}"]}
    except etree.DocumentInvalid as e:
        return {"valid": False, "errors": [f"Document Invalid Error: {e}"]}

@app.route('/', methods=['GET'])
def validate_route():
        # Paths to the XML and XSD files
    xml_file_path = 'test.xml'

    # Read the XML and XSD files
    xml_content = read_file(xml_file_path)
    

    # Validate the XML content against the XSD schema
    result = validate_xml(xml_content)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)