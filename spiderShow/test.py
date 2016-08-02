import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.py')
print config.get('redis', 'REDIS_SERVER')


