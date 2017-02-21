#!/usr/bin/env python3
import time

from cozify import hub, multisensor
from cozifytemp import storage

sensors = []
while True:
    data = hub.getDevices()
    sensors = multisensor.getMultisensorData(data)
    try:
        storage.storeMultisensor(sensors)
    except:
        print('Issues writing to InfluxDB')
    else:
        # write succeeded, drop cache
        sensors = []
    time.sleep(5)
