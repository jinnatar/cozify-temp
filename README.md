# cozify-temp
Pull Proove multisensor data from Cozify Hub into InfluxDB

Authentication is handled by python-cozify bindings developed separately: [github.com/Artanicus/python-cozify](https://github.com/Artanicus/python-cozify)

## installation
- sudo pip3 install cozify (or install manually from: [github.com/Artanicus/python-cozify](https://github.com/Artanicus/python-cozify))
- cp main.cfg.dist main.cfg
- edit main.cfg to contain your InfluxDB parameters
- run cozify-single-sample.py to get a single snapshot and push it to InfluxDB.
- if a single sample was fine, run cozify-sample-loop.py to get and push data on a 5s interval

![example Grafana graphs][graphs]

[graphs]: https://i.imgur.com/TwrfXES.png "example Grafana graphs"
