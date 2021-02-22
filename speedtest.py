import os
import re
import subprocess
import time
from influxdb import InfluxDBClient

response = subprocess.Popen('/usr/bin/speedtest', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

print(response)

ping = re.search('Latency:\s+(.*?)\s', response, re.MULTILINE)
download = re.search('Download:\s+(.*?)\s', response, re.MULTILINE) 
upload = re.search('Upload:\s+(.*?)\s', response, re.MULTILINE)
packetloss = re.search('Packet Loss:\s+(.*?)\s', response, re.MULTILINE)

print(packetloss)

ping = ping.group(1)
download = download.group(1)
upload = upload.group(1)

if packetloss != "Not":
    packetloss = packetloss.group(1)
else:
    packetloss = "0%"

speed_data = [
    {
        "measurement": "internet_speed",
        "tags": {
            "host": "RaspPi4"
        },
        "fields": {
            "download": float(download),
            "upload": float(upload),
            "packetloss": float(packetloss.strip('%')) / 100.0,
            "ping": float(ping)
        }
    }
]

client = InfluxDBClient('localhost', 8086, 'speedmonitor', 'speedmonitor', 'internetspeedmonitor')
client.write_points(speed_data)

try:
    f = open('/development/speedtest/speedtest.csv', 'a+')
    if os.stat('/development/speedtest/speedtest.csv').st_size == 0:
        f.write('Date,Time,Ping (ms),Jitter (ms),Download (Mbps),Upload (Mbps)\r\n')
except:
    pass

f.write('{},{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, packetloss, download, upload))

