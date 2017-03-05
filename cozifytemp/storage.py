from influxdb import InfluxDBClient
from influxdb import SeriesHelper

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
        precision = 'ms'


# expects list of maps: [{name: 'foo', temperature: 42, humidity: 30}, ...]
def storeMultisensor(sensors):
    for sensor in sensors:
        # time comes in milliseconds, influxDB expects nanoseconds
        MultisensorSeries(name=sensor['name'], temperature=sensor['temperature'], humidity=sensor['humidity'], time=sensor['time'])
        print('%s: %s, %s C, %s %%H' %(sensor['time'], sensor['name'], sensor['temperature'], sensor['humidity']))
    MultisensorSeries.commit()
