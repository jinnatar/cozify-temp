import datetime

from absl import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from . import config as c

sensor_types = {"temperature": "C", "humidity": "%RH"}

client = InfluxDBClient(
    url=c.config["Storage"]["url"],
    token=c.config["Storage"]["token"],
    org=c.config["Storage"]["organization"],
)

bucket = c.config["Storage"]["bucket"]

write_api = client.write_api(write_options=SYNCHRONOUS)


# sensors expects list of maps: [{name: 'foo', temperature: 42, humidity: 30}, ...]
def store_sensor_data(sensors, tz=datetime.timezone.utc, verbose=False):
    sequence = []
    for sensor in sensors:
        # time is confusing:
        # - cozify provides time in milliseconds
        # - influxDB internally stores as microseconds
        # - python-influxdb is finicky with int format timestamps,
        # hence datetime object works best.
        # also need to make sure we interpret the timestamp as UTC!
        # but when printing we want Hub timezone.
        time = datetime.datetime.fromtimestamp(
            sensor["lastSeen"] / 1000, tz=datetime.timezone.utc
        )
        name = sensor["name"]
        for type, unit in sensor_types.items():
            value = sensor[type]
            if value:
                point = (
                    Point(type)
                    .tag("name", name)
                    .field("value", value)
                    .time(time, WritePrecision.MS)
                )
                sequence.append(point)
                infoline = f"[{time.astimezone(tz)}] {name}: {value} {unit}"
                if verbose:
                    print(infoline)
                else:
                    logging.info(infoline)
    write_api.write(bucket=bucket, record=sequence)
    return len(sequence)
