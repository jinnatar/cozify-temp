#!/usr/bin/env python3
import time

from cozify import cloud, hub, multisensor
from cozify-temp import storage

while True:
    data = hub.getDevices()
    sensors = multisensor.getMultisensorData(data)
    storage.storeMultisensor(sensors)
    time.sleep(5)
