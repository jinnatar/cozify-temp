# cozify-temp
Pull sensor data from Cozify Hub into InfluxDB. At current temperature & humidity data is supported but expanding that is trivial.

Authentication and other Cozify details are handled by python-cozify bindings developed separately: [github.com/Artanicus/python-cozify](https://github.com/Artanicus/python-cozify) but this repo acts as an official example.

## Installation

If you just want to use it:
```
pip3 install cozifytemp
cozifytemp-single-sample # perform the first time authentication and create a default config. Storage will fail if you don't have a local InfluxDB instance!
# edit ~/.config/cozify-temp/influxdb.cfg to match your infuxdb location if needed
cozifytemp-sample-loop # pull & store data in a loop.
```

If you want to experiment with the code:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
git clone https://github.com/Artanicus/cozify-temp
cd cozify-temp
poetry install
poetry run cozifytemp-single-sample
poetry run cozifytemp-sample-loop
```

## Configuration

- For storage, create a InfluxDB bucket called for example `cozify`. You will also need to configure your organization and generate a token that has write access to the bucket.
- The easiest way is to use the web interface of InfluxDB 2.0 by navigating to http://localhost:8086 or which ever hostname your InfluxDB server is hosted at.
- Run `cozifytemp-single-sample`. It won't work but you'll generate the default config to modify.
- Edit ~/.config/cozify-temp/influxdb.cfg to include your DB url, token, organization and bucket names.
- Test connection by running `cozifytemp-single-sample` to get a single snapshot and push it to InfluxDB. The single-sample script is more naive but simpler to get started with.
- if a single sample was fine, run `cozifytemp-sample-loop` to get and push data on a 60s interval. The loop script is more robust than the single sample and is usable as a systemd daemon.
- To explore all options run `cozifytemp-sample-loop --help`

## Docker

The image is published on GitHub at [ghcr.io/artanicus/cozify-temp](https://ghcr.io/artanicus/cozify-temp) As with other methods of running, first run a single sample run to init config, edit the generated infuxdb config and then run the long-term sampler.
```
docker pull ghcr.io/artanicus/cozify-temp:latest
docker run -v /path/to/persistent/config:/root/.config/ -it cozify-temp:latest cozifytemp-single-sample # interactive run to initialize config & authenticate
docker run -v /path/to/persistent/config:/root/.config/ cozify-temp:latest # long term sampler
```

![example Grafana graphs][graphs]

[graphs]: https://i.imgur.com/TwrfXES.png "example Grafana graphs"
