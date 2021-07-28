#!/usr/bin/env python3

from cozify import hub, cloud
from cozifytemp import storage, config, util
from influxdb_client.rest import ApiException
import pytz, time

# Get all temperature and humidity capable data
# This version is only compatible with python-cozify >= v0.2.11 since it relies on the new capabilities features
def main():
    cloud.authenticate()
    sensors = hub.devices(capabilities= [
        hub.capability.TEMPERATURE,
        hub.capability.HUMIDITY]
        )
    tz=pytz.timezone(hub.tz()) # Only used to print timezones nice, storage is always in UTC!
    try:
        storage.store_sensor_data(util.homogenize(sensors), tz=tz, verbose=True)
    except:
        print('Storage call failed, you may want to edit the db config at: %s' % config.config_file)
        raise
    else:
         print('write(%s) successful!' % len(sensors))

if __name__ == "__main__":
    main()
