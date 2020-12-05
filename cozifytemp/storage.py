import datetime
from absl import logging
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "rDXfwuTAj3h8VsrvNsiovi8Cx5DK43tW-FWUG_Da9dYKHh5NYY93ai6cbiHt4GgjsjEeoiGZ-j0wBxnFfPjRhQ=="
org = "Arcadia"
bucket = "cozify"

sensor_types = {
        'temperature': 'C',
        'humidity': '%RH'
        }

from . import config as c

client = InfluxDBClient(
        url=c.config['Storage']['url'],
        token=c.config['Storage']['token'],
        org=c.config['Storage']['organization']
)

write_api = client.write_api(write_options=SYNCHRONOUS)

# sensors expects list of maps: [{name: 'foo', temperature: 42, humidity: 30}, ...]
def store_sensor_data(sensors, tz=datetime.timezone.utc, verbose=False):
    sequence = []
    for sensor in sensors:
        # time is confusing:
        # - cozify provides time in milliseconds
        # - influxDB internally stores as microseconds
        # - python-influxdb is finicky with int format timestamps, hence datetime object works best
        # also need to make sure we interpret the timestamp as UTC!
        # but when printing we want Hub timezone.
        time=datetime.datetime.fromtimestamp(sensor['lastSeen']/1000, tz=datetime.timezone.utc)
        name=sensor['name']
        for type, unit in sensor_types.items():
            value=sensor[type]
            if value:
                point = Point(type).tag('name', name).field('value', value).time(time, WritePrecision.MS)
                sequence.append(point)
                infoline = '[{time}] {name}: {value} {unit}'.format(
                        time=time.astimezone(tz),
                        unit=unit,
                        type=type,
                        name=name,
                        value=value,
                        )
                if verbose:
                    print(infoline)
                else:
                    logging.info(infoline)
    write_api.write(bucket, org, sequence)
    return len(sequence)
