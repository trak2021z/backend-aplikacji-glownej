from pymemcache.client import base
import psutil

client = base.Client(('localhost', 11211))
client.set('CPU_USAGE', psutil.cpu_percent())

while True:
    print(client.get('CPU_USAGE'))
    cpu_usage = psutil.cpu_percent(interval=30.0)
    client.set('CPU_USAGE', cpu_usage)