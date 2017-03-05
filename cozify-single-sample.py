#!/usr/bin/env python3

from cozify import hub, multisensor
from cozifytemp import storage

# very naive example pulling a single sample and storing it
def main():
    data = hub.getDevices()
    sensors = multisensor.getMultisensorData(data)
    storage.storeMultisensor(sensors)

if __name__ == "__main__":
    main()
