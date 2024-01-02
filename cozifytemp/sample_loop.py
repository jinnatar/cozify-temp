#!/usr/bin/env python3
import signal
import sys
import time

import pytz
from absl import app, flags, logging
from cozify import cloud, hub
from cozify.Error import APIError
from influxdb_client.rest import ApiException

from cozifytemp import cache, storage, util

FLAGS = flags.FLAGS

flags.DEFINE_integer(
    "frequency", 60, "How many seconds to wait between sensor reads", lower_bound=1
)
flags.DEFINE_integer(
    "tolerance_read", 10, "How many consecutive read errors are fine", lower_bound=0
)
flags.DEFINE_integer(
    "tolerance_write", 10, "How many consecutive write errors are fine", lower_bound=0
)


def main(argv):
    global sensors
    error_counter_read = 0
    error_counter_write = 0

    # Grab hub timezone for display of timestamps. Data is always recorded in UTC!
    tz = pytz.timezone(hub.tz())

    # loop until interrupted, can be for example run as a systemd service
    while True:
        # cozify.hub.devices will return the raw devices API call blob as a dictionary
        # if anything fails the library will throw an APIError exception.
        try:
            # Check hub & cloud connectivity and have it auto-renewed
            hub.ping()
            # Cloud checking is needed since the loop will run for a long time
            # unattended and cloud tokens expire every 28 days.
            cloud.ping()

            # Get all devices that have a temperature OR humidity capability.
            # Homogenize it to not have holes in the data.
            data = util.homogenize(
                hub.devices(
                    capabilities=[hub.capability.TEMPERATURE, hub.capability.HUMIDITY]
                )
            )
        except APIError as e:
            error_counter_read += 1
            logging.error(
                f"Failed to get sensor data({error_counter_read}/{FLAGS.tolerance_read}).\
                Error code: {e.status_code}, error: {e}"
            )
            if error_counter_read > FLAGS.tolerance_read:
                raise  # Too many errors, let it burn to the ground
        else:  # data retrieval succeeded
            error_counter_read = 0
            # Data is extended into the list so that any previous cache is preserved
            sensors.extend(data)

        # attempt storage if we have any to store
        if len(sensors) > 0:
            # InfluxDB writes can fail if for example IO conditions are bad
            # to mitigate this, we'll cache results and try again on the next
            # loop with both old & new data
            try:
                data_length = storage.store_sensor_data(sensors, tz=tz)
            except ApiException as e:
                error_counter_write += 1
                logging.warning(
                    f"Unable to write to InfluxDB\
                    ({error_counter_write}/{FLAGS.tolerance_write}): \
                    {e}. Data kept in cache({len(sensors)}) for next write cycle."
                )
                if error_counter_write > FLAGS.tolerance_write:
                    raise  # Too many errors, let it burn to the ground
            else:
                # write succeeded, drop cache
                logging.info(
                    f"write(sensors: {len(sensors)}, datapoints: {data_length}) successful!"
                )
                error_counter_write = 0
                sensors = []
                cache.clear()
        else:
            logging.error("No sensors found to log.")
        time.sleep(FLAGS.frequency)


# Handle cache dumping if killed.
def cleanup():
    global sensors
    if len(sensors) > 0:
        cache.dump(sensors)
        logging.warning("SIGTERM, dumped cache to file")
    else:
        logging.info("SIGTERM, no cache to dump")
    sys.exit()


def sigterm_handler(signal, frame):
    cleanup()


sensors = []  # used as a cache for sensor data
if cache.exists():  # populate any existing cache dump
    logging.info("Found cache from disk, adding it to in-memory cache")
    data = cache.read()
    if data:
        sensors.extend(cache.read())


def run():
    signal.signal(signal.SIGTERM, sigterm_handler)
    try:
        app.run(main)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    run()
