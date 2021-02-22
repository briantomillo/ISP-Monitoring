import subprocess
import time
import re
import os
from influxdb import InfluxDBClient

hostname = "8.8.8.8"
pingResponse = subprocess.Popen("ping -q -i 1 -c 20 " + hostname, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

rtt_min = re.search('=.(\d.*?)\/', pingResponse, re.MULTILINE)
rtt_avg = re.findall('(\d.*?)\/', pingResponse, re.MULTILINE)
rtt_max = re.findall('(\d.*?)\/', pingResponse, re.MULTILINE)
dnsPacketLoss = re.search('received,.(.*\d%)', pingResponse, re.MULTILINE)

try:
    rtt_min = rtt_min.group(1)
    rtt_avg = rtt_avg[1]
    rtt_max = rtt_max[2]
except:
    print('No output RTT response from ping')
    rtt_min = 0
    rtt_avg = 0
    rtt_max = 0

print(dnsPacketLoss)
dnsPacketLoss = dnsPacketLoss.group(1)
print(dnsPacketLoss)

dns_ping_data = [
    {
        "measurement": "dns_ping",
        "tags": {
            "host": "RaspPi4"
        },
        "fields": {
            "rtt_min": float(rtt_min),
            "rtt_avg": float(rtt_avg),
            "rtt_max": float(rtt_max),
            "dnsPacketLoss": float(dnsPacketLoss.strip('%')) / 100.0
        }
    }
]

client = InfluxDBClient('localhost', 8086, 'speedmonitor', 'speedmonitor', 'dnsmonitor')
client.write_points(dns_ping_data)
