#!/usr/bin/env python3

from cozify import hub
from cozifytemp import storage, config
from influxdb.exceptions import InfluxDBServerError
import pytz, time

# experimental example of using the new python-cozify=0.2.10 capability filtering
def main():
    temp_sensors = hub.devices(capability=hub.capability.TEMPERATURE)
    hygro_sensors = hub.devices(capability=hub.capability.HUMIDITY)
    sensors = temp_and_hygro(temp_sensors, hygro_sensors)
    tz=pytz.timezone(hub.tz())
    try:
        storage.storeMultisensor(sensors, tz=tz)
    except:
        print('Storage call failed, you may want to edit the db config at: %s' % config.config_file)
        raise
    else:
         print('write(%s) successful!' % len(sensors))

# Data smasher to make the new device filtering logic still work with old storage logic
def temp_and_hygro(temp_sensors, hygro_sensors):
    out = {}
    print(type(temp_sensors))
    for device_id, device in temp_sensors.items():
        if device_id not in out:
            out[device_id] = {}
        out[device_id]['name'] = device['name']
        out[device_id]['temperature'] = device['state']['temperature']
        out[device_id]['humidity'] = None # set them to None, the next loop will write in values where we have them
        if 'lastSeen' in device['state']:
            out[device_id]['time'] = device['state']['lastSeen']
        else:
            out[device_id]['time'] = time.time() * 1000

    for device_id, device in hygro_sensors.items():
        if device_id not in out:
            out[device_id] = {}
        out[device_id]['name'] = device['name']
        out[device_id]['humidity'] = device['state']['humidity']
        if 'lastSeen' in device['state']:
            out[device_id]['time'] = device['state']['lastSeen']
        else:
            out[device_id]['time'] = time.time() * 1000

    return list(out.values())

if __name__ == "__main__":
    main()
