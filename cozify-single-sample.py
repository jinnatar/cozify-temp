#!/usr/bin/env python3

from cozify import hub
from cozifytemp import storage, config
from influxdb.exceptions import InfluxDBServerError
import pytz, time

# Get all temperature and humidity capable data
# This version is only compatible with python-cozify >= v0.2.11 since it relies on the new capabilities features
def main():
    sensors = hub.devices(capabilities=[hub.capability.TEMPERATURE, hub.capability.HUMIDITY])
    tz=pytz.timezone(hub.tz())
    try:
        storage.storeMultisensor(conv(sensors), tz=tz)
    except:
        print('Storage call failed, you may want to edit the db config at: %s' % config.config_file)
        raise
    else:
         print('write(%s) successful!' % len(sensors))

# Data smasher to fill in the gaps of what we didn't get from the devices
def conv(sensors):
    out = {}
    for device_id, device in sensors.items():
        if device_id not in out:
            out[device_id] = {}
        out[device_id]['name'] = device['name']

        for key, default in {
                'temperature': None,
                'humidity': None,
                'lastSeen': int(time.time()*1000)
                }.items():
            if key in device['state']:
                out[device_id][key] = device['state'][key]
            else:
                out[device_id][key] = default
    return list(out.values())

if __name__ == "__main__":
    main()
