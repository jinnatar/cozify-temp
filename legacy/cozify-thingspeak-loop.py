#!/usr/bin/env python3
import datetime
import logging
import signal
import sys
import time

import thingspeak
from cozify import cloud, hub
from cozify.Error import APIError

from cozifytemp import cache, storage, util

""" A very unfinished and crude example of writing temperature data into thingspeak.
It sort of works but doesn't handle multiple sensors in the way that thingspeak expects.
"""

channel = 42
api_key = "foobar"
write_key = "barfoo"


def main():
    global sensors
    # loop until interrupted, can be for example run as a systemd service

    # Initialize thingspeak channel
    ch = thingspeak.Channel(channel, api_key=api_key, write_key=write_key)

    while True:
        try:
            # Check connectivity and have it auto-renewed if it's deemed time to do so.
            cloud.ping()
            # Get all devices that have a temperature OR humidity capability.
            # Homogenize it to not have holes in the data.
            data = util.homogenize(
                hub.devices(
                    capabilities=[hub.capability.TEMPERATURE, hub.capability.HUMIDITY]
                )
            )
        except APIError as e:
            if e.status_code == 401:  # auth failed
                logging.warning("Auth failed, this should not happen.")
            else:
                raise  # we ignore all other APIErrors and let it burn to the ground
        else:  # data retrieval succeeded
            # Change format to match that of ThingSpeak
            for sensor in data:
                # Data is appended into the list so that any previous cache is preserved and these are just added as new samples
                sensors.append(
                    {
                        "created_at": datetime.datetime.fromtimestamp(
                            int(sensor["lastSeen"] / 1000)  # milliseconds to seconds
                        ).isoformat(),
                        "field1": sensor["temperature"],
                        "field2": sensor["humidity"],
                    }
                )

        # attempt storage if we have any to store
        if len(sensors) > 0:
            print("writing to ThingSpeak...")
            print(sensors)
            try:
                for sensor in sensors:
                    ch.update(sensor)
            except:
                print("write(%s) failed, data kept in cache." % len(sensors))
            else:
                # write succeeded, drop cache
                print("write(%s) successful!" % len(sensors))
                sensors = []
                cache.clear()

        time.sleep(60)


# Handle cache dumping if killed.
def sigterm_handler(signal, frame):
    global sensors
    if len(sensors) > 0:
        cache.dump(sensors)
        logging.critical("SIGTERM, dumped cache to file")
    else:
        logging.critical("SIGTERM, no cache to dump")
    sys.exit(1)


sensors = []  # used as a cache for sensor data
if cache.exists():  # populate any existing cache dump
    sensors.extend(cache.read())

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)
    main()
