# dark-chess

## Description
Chess with fog of war ([game rules](https://en.wikipedia.org/wiki/dark_chess))
There are two servers:
- app.py - web backend of game, interface is [REST](http://rest.elkstein.org/).
- websocket.py - websocket server, which sends game events as opponent moves to client.

## Requirements
- [python 3.4+](https://www.python.org/download/releases/3.4.0/)
- [redis](http://redis.io/download)
- [celery](http://www.celeryproject.org/install/)
- [peewee compatible DBMS server](http://docs.peewee-orm.com/en/latest/peewee/database.html#vendor-specific-parameters)

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
$ python websocket.py
```

## Testing
```bash
$ cd dark-chess
$ python -m unittest tests
```

## Documentation
https://github.com/AHAPX/dark-chess/wiki/
