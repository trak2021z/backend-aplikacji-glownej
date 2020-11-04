from pymemcache.client import base
import psutil
from datetime import datetime
import json

client = base.Client(('localhost', 11211))
client.set('CPU_USAGE', json.dumps({'usage': psutil.cpu_percent(), 'timestamp': datetime.now()}, default=str))
while True:
    print(client.get('CPU_USAGE'))
    cpu_usage = psutil.cpu_percent(interval=30.0)
    client.set('CPU_USAGE', json.dumps({'usage': cpu_usage, 'timestamp': datetime.now()}, default=str))
