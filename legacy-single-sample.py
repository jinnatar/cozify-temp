#!/usr/bin/env python3

from cozify import hub, multisensor
from cozifytemp import storage, config
from influxdb.exceptions import InfluxDBServerError
import pytz

# very naive example pulling a single sample and storing it
def main():
    data = hub.getDevices()
    sensors = multisensor.getMultisensorData(data)
    tz=pytz.timezone(hub.tz())
    try:
        storage.storeMultisensor(sensors, tz=tz)
    except:
        print('Storage call failed, you may want to edit the db config at: %s' % config.config_file)
        raise
    else:
         print('write(%s) successful!' % len(sensors))

if __name__ == "__main__":
    main()
