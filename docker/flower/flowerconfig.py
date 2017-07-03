# Broker settings
broker_url = 'amqp://guest:guest@rabbit:5672//'

# RabbitMQ management api
broker_api = 'http://guest:guest@rabbit:15672/api/'

# Enable debug logging
logging = 'DEBUG'

# Web server address
address = '0.0.0.0'

# Refresh dashboards automatically
auto_refresh = True

# Run the http server on a given port
port = 5555

# Enable support of X-Real-Ip and X-Scheme headers
xheaders = True

# A database file to use if persistent mode is enabled
db = '/var/flower/db/flower.db'

# Enable persistent mode. If the persistent mode is enabled Flower saves the current state and reloads on restart
persistent = True
