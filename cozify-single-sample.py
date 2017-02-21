#!/usr/bin/env python3

from cozify import hub, multisensor
from cozifytemp import storage

data = hub.getDevices()
sensors = multisensor.getMultisensorData(data)
storage.storeMultisensor(sensors)
