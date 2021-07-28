#!/usr/bin/env python3
import sys
import time
import csv

from cozifytemp import storage

from influxdb.exceptions import InfluxDBServerError

def main(argv):
    csvpath=argv[1]
    sensors = []

    with open(csvpath, 'rt') as csvfile:
        sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in sreader:
            print(row)
            sensors.append(
                    {
                        'time': int(row[0]), 
                        'name': row[1], 
                        'temperature': float(row[2]), 
                        'humidity': int(row[3]) if row[3] != 'None' else None
                        }
                    )

    # InfluxDB writes can fail if for example IO conditions are bad
    try:
        storage.storeMultisensor(sensors)
    except InfluxDBServerError:
        print('Data set size: %s, issues writing to InfluxDB' % (len(sensors)))
        pass
    else:
        print('write(%s) successful!' % len(sensors))


if __name__ == "__main__":
    main(sys.argv)
