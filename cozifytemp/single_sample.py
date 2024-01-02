#!/usr/bin/env python3

import pytz
from cozify import cloud, hub

from cozifytemp import config, storage, util


# Get all temperature and humidity capable data
# This version is only compatible with python-cozify >= v0.2.11,
# since it relies on the new capabilities features.
def main():
    cloud.authenticate()
    sensors = hub.devices(
        capabilities=[hub.capability.TEMPERATURE, hub.capability.HUMIDITY]
    )

    # Only used to print timezones nice, storage is always in UTC!
    tz = pytz.timezone(hub.tz())
    try:
        storage.store_sensor_data(util.homogenize(sensors), tz=tz, verbose=True)
    except:
        print(
            "Storage call failed, you may want to edit the db config at: %s"
            % config.config_file
        )
        raise
    else:
        print("write(%s) successful!" % len(sensors))


if __name__ == "__main__":
    main()
