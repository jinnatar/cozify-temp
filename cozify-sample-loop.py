#!/usr/bin/env python3
import time

from cozify import cloud, hub, multisensor, storage

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
