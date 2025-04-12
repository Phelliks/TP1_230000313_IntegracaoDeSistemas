import requests

# URL do serviço SOAP
SOAP_URL = "http://127.0.0.1:5000/soap"

# Criar uma requisição SOAP para somar dois números
numero1 = 5
numero2 = 10

soap_request = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>
        <numero1>{numero1}</numero1>
        <numero2>{numero2}</numero2>
    </soapenv:Body>
</soapenv:Envelope>"""

# Enviar a requisição para o servidor
headers = {'Content-Type': 'text/xml'}
response = requests.post(SOAP_URL, data=soap_request, headers=headers)

# Exibir a resposta
print("Resposta do Servidor:")
print(response.text)
