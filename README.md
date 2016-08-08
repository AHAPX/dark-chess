# dark-chess

## Description
Chess with fog of war ([game rules](https://en.wikipedia.org/wiki/dark_chess))
There are two servers:
- app.py - web backend of game, interface is [REST](http://rest.elkstein.org/).
- websocket.py - websocket server, which sends game events as opponent moves to client.

## Requirements
- [python 3.3+](https://www.python.org/download/releases/3.3.0/)
- [redis](http://redis.io/download)
- [peewee compatible DBMS server](http://docs.peewee-orm.com/en/latest/peewee/database.html#vendor-specific-parameters)
- [websocket](https://github.com/AHAPX/websocket) - not required, but recommended
- [smtpush](https://github.com/AHAPX/smtpush) - not required, but recommended

## Installation
```bash
$ git clone https://github.com/AHAPX/dark-chess
$ cd dark-chess
$ pip install -r requirements.txt
$ cp src/config_local.py.sample src/config_local.py
```

## Usage
```bash
$ cd dark-chess/src
$ python main.py
```

## Testing
```bash
$ cd dark-chess
$ python -m unittest tests
```

## Documentation
https://github.com/AHAPX/dark-chess/wiki/
