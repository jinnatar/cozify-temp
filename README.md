# cozify-temp
Pull Proove multisensor data from Cozify Hub into InfluxDB

Authentication is handled by python-cozify bindings developed separately: [github.com/Artanicus/python-cozify](https://github.com/Artanicus/python-cozify)

## installation
- Install dependencies:

```
sudo pip3 install cozify pytz
```

- For storage, create a InfluxDB database called 'cozify':

```
influx -execute 'CREATE DATABASE cozify'
```

- Test connection by running cozify-single-sample.py to get a single snapshot and push it to InfluxDB. The single-sample script is more naive but simpler to get started with.
- If you so choose, customize db connection parameters in ~/.config/cozify-temp/influxdb.cfg (config created with defaults at first runtime)
- if a single sample was fine, run cozify-sample-loop.py to get and push data on a 5s interval. The loop script is more robust than the single sample.

![example Grafana graphs][graphs]

[graphs]: https://i.imgur.com/TwrfXES.png "example Grafana graphs"
