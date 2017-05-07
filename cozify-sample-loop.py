#!/usr/bin/env python3
import time, logging

from cozify import hub, cloud, multisensor
from cozifytemp import storage

from influxdb.exceptions import InfluxDBServerError
from cozify.Error import APIError


def main():
    sensors = [] # used as a cache for sensor data

    # loop until interrupted, can be for example run as a systemd service
    while True:
        # cozify.hub.getDevices will return the raw devices API call blob as a dictionary
        # it will also trigger cozify.cloud.authentication() if we don't have a valid hub key yet.
        # if auth fails it will throw an APIError exception and kill this loop, so we need to check for that
        try:
            data = hub.getDevices()
        except APIError as e:
            if e.status_code == 401: # auth failed
                logging.warning('Auth expired, attempting transparent renew')
                cloud.authenticate(trustHub=False) # we shortcircuit some tests by already telling it to renew hub
            else:
                raise # we ignore all other APIErrors and let it burn to the ground
        else: # data retrieval succeeded
            # cozify.multisensor.getMultisensorData will take the raw device blob and
            # extract a list of dictionaries [{temp, humidity, time}, ...] of all the multisensor devices
            # Data is extended into the list so that any previous cache is preserved and these are just added as new samples
            sensors.extend(multisensor.getMultisensorData(data))

        # attempt storage if we have any to store
        if len(sensors) > 0:
            # InfluxDB writes can fail if for example IO conditions are bad
            # to mitigate this, we'll cache results and try again on the next loop with both old & new data
            try:
                print('writing to InfluxDB...')
                storage.storeMultisensor(sensors)
            except InfluxDBServerError:
                print('Data kept in cache(%s), issues writing to InfluxDB' % (len(sensors)))
            else:
                # write succeeded, drop cache
                print('write(%s) successful!' % len(sensors))
                sensors = []
        time.sleep(60)


if __name__ == "__main__":
    main()
