#!/usr/bin/env python3
import time

from cozify import hub, multisensor
from cozifytemp import storage

from influxdb.exceptions import InfluxDBServerError

def main():
    sensors = []

    # loop until interrupted
    while True:
        # cozify.hub.getDevices will return the raw devices API call blob as a dictionary
        # it will also trigger cozify.cloud.authentication() if we don't have a valid hub key yet.
        # if auth fails it will throw an exception and kill this loop
        data = hub.getDevices()

        # cozify.multisensor.getMultisensorData will take the raw device blob and
        # extract a list of dictionaries [{temp, humidity, time}, ...] of all the multisensor devices
        # Data is extended into the list so that any previous cache is preserved and these are just added as new samples
        sensors.extend(multisensor.getMultisensorData(data))

        # InfluxDB writes can fail if for example IO conditions are bad
        # to mitigate this, we'll cache results and try again on the next loop with both old & new data
        try:
            print('writing to InfluxDB...')
            storage.storeMultisensor(sensors)
        except InfluxDBServerError():
            print('Data kept in cache(%s), issues writing to InfluxDB' % (len(sensors)))
        else:
            # write succeeded, drop cache
            print('write(%s) successful!' % len(sensors))
            sensors = []
        time.sleep(60)


if __name__ == "__main__":
    main()
