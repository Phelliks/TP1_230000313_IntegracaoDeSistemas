from flask import Flask, request, Response
import xmlschema
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Carregar o esquema XSD para validação
xsd_path = "./Servidor/Soap/schema.xsd"
try:
    xsd_schema = xmlschema.XMLSchema(xsd_path)
except Exception as ex:
    print(f"Erro ao carregar o XSD: {ex}")
    exit(1)

def calcular_operacao(operacao, num1, num2):
    """
    Realiza a operação aritmética especificada.
    """
    operacao = operacao.lower().strip()
    if operacao == "soma":
        return num1 + num2
    elif operacao == "subtracao":
        return num1 - num2
    elif operacao == "multiplicacao":
        return num1 * num2
    elif operacao == "divisao":
        if num2 == 0:
            raise ZeroDivisionError("Divisão por zero não permitida!")
        return num1 / num2
    else:
        raise ValueError("Operação inválida! Use: soma, subtracao, multiplicacao ou divisao.")

@app.route('/soap', methods=['POST'])
def soap_service():
    xml_request = request.data.decode('utf-8')
    
    try:
        # Validação: Se o XML não for válido, is_valid() retornará False
        if not xsd_schema.is_valid(xml_request):
            validation_errors = "\n".join([str(e) for e in xsd_schema.iter_errors(xml_request)])
            raise ValueError(f"Erro na validação XSD:\n{validation_errors}")

        # Convertendo o XML usando o ElementTree
        root = ET.fromstring(xml_request)
        # Consideramos que o XML tem a estrutura: Envelope -> Body -> OperacaoRequest -> (operacao, numero1, numero2)
        # (Sem namespaces – caso contrário, é necessário tratar os namespaces.)
        operacao_req = root.find('./Body/OperacaoRequest')
        if operacao_req is None:
            raise ValueError("OperacaoRequest não encontrado.")

        operacao = operacao_req.findtext("operacao")
        numero1 = int(operacao_req.findtext("numero1"))
        numero2 = int(operacao_req.findtext("numero2"))

        # Efetua a operação aritmética
        resultado = calcular_operacao(operacao, numero1, numero2)

        # Constrói a resposta SOAP
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <OperacaoResponse>
      <resultado>{resultado}</resultado>
    </OperacaoResponse>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(response_xml, mimetype='text/xml')

    except Exception as e:
        # Cria uma resposta SOAP com o Fault para o erro
        fault_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <soapenv:Fault>
      <faultcode>SOAP-ENV:Client</faultcode>
      <faultstring>{str(e)}</faultstring>
    </soapenv:Fault>
  </soapenv:Body>
</soapenv:Envelope>"""
        return Response(fault_response, status=400, mimetype='text/xml')

if __name__ == '__main__':
    print("Servidor SOAP avançado rodando em http://127.0.0.1:5000/soap")
    app.run(host='127.0.0.1', port=5000)
