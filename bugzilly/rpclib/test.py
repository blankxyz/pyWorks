from suds.client import Client
from suds.transport.https import HttpAuthenticated

t = HttpAuthenticated(username='songyq@ehr.com', password='314159')
test = Client('http://127.0.0.1:8080/WebService/ws/DeviceManageService?wsdl', transport=t)

print test