import suds

url = 'http://localhost:8080/test/calc?wsdl'
# url = 'http://10.3.18.44:8080/test/calc?wsdl'
client = suds.client.Client(url)
service = client.service

print client

sum_result = service.sum(10, 34)
print sum_result
print client.last_received()

multiply_result = service.multiply(5, 5)
print multiply_result
print client.last_received()