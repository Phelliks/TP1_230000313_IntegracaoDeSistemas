from flask import Flask, request, Response
import xmlschema

app = Flask(__name__)

# Carregar o esquema XSD para validação
xsd_path = "./Servidor/Soap/schema.xsd"
xsd_schema = xmlschema.XMLSchema(xsd_path)

@app.route('/soap', methods=['POST'])
def soap_service():
    """
    Serviço SOAP com validação XSD para somar dois números.
    """
    xml_request = request.data.decode('utf-8')
    
    try:
        # Validar o XML recebido contra o esquema XSD
        if not xsd_schema.is_valid(xml_request):
            error_message = f"Erro na validação XSD: {xsd_schema.validate(xml_request)}"
            raise ValueError(error_message)
        
        # Após validação, extrai os valores de <numero1> e <numero2>
        numero1 = int(xml_request.split('<numero1>')[1].split('</numero1>')[0])
        numero2 = int(xml_request.split('<numero2>')[1].split('</numero2>')[0])
        
        # Calcula a soma
        resultado = numero1 + numero2
        
        # Construir a resposta SOAP em XML
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <resultado>{resultado}</resultado>
            </soapenv:Body>
        </soapenv:Envelope>"""
        return Response(response_xml, mimetype='text/xml')
    
    except Exception as e:
        # Retornar erro em formato SOAP em caso de exceção
        error_response = f"""<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <soapenv:Fault>
                    <faultcode>SOAP-ENV:Client</faultcode>
                    <faultstring>{str(e)}</faultstring>
                </soapenv:Fault>
            </soapenv:Body>
        </soapenv:Envelope>"""
        return Response(error_response, status=400, mimetype='text/xml')

if __name__ == '__main__':
    print("Servidor Flask rodando em http://127.0.0.1:5000/soap")
    app.run(host='127.0.0.1', port=5000)
