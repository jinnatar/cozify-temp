from influxdb import InfluxDBClient
from influxdb import SeriesHelper
import datetime


from . import config as c

db = InfluxDBClient(
        c.config['Storage']['host'],
        c.config['Storage']['port'],
        c.config['Storage']['user'],
        c.config['Storage']['password'],
        c.config['Storage']['db']
)

# helper class for defining the type of series data stored in influxDB
class MultisensorSeries(SeriesHelper):
    class Meta:
        client = db
        series_name = 'multisensor'
        fields = ['temperature', 'humidity']
        tags = ['name']


# sensors expects list of maps: [{name: 'foo', temperature: 42, humidity: 30}, ...]
def storeMultisensor(sensors, tz=datetime.timezone.utc, verbose=True):
    for sensor in sensors:
        # time is confusing:
        # - cozify provides time in milliseconds
        # - influxDB internally stores as microseconds
        # - python-influxdb is finicky with int format timestamps, hence datetime object works best
        # also need to make sure we interpret the timestamp as UTC!
        # but when printing we want Hub timezone.
        time=datetime.datetime.fromtimestamp(sensor['lastSeen']/1000, tz=datetime.timezone.utc)

        MultisensorSeries(name=sensor['name'], temperature=sensor['temperature'], humidity=sensor['humidity'], time=time)
        if verbose:
            print('[%s] %s: %s, %s C, %s %%H' %(sensor['lastSeen'], time.astimezone(tz), sensor['name'], sensor['temperature'], sensor['humidity']))
    MultisensorSeries.commit()
