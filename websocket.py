import sys
import traceback
import asyncio
import json
import logging
from functools import partial

import websockets
import asyncio_redis

import config


logger = logging.getLogger(__name__)


class Client():
    _socket = None
    _tags = []

    def __init__(self, socket):
        self._socket = socket

    def send(self, message):
        if self._socket and self._socket.open:
            if not isinstance(message, str):
                try:
                    message = json.dumps(message)
                except:
                    message = str(message)
            yield from self._socket.send(message)

    def init_tags(self, tags):
        self._tags = tags

    def is_active(self):
        return self._socket and self._socket.open

    def is_tag(self, tag):
        return tag in self._tags

    def name(self):
        return ', '.join(self._tags)


class Clients():
    _clients = []

    def add_client(self, client):
        if client.is_active():
            self._clients.append(client)

    def send(self, message, tags=[]):
        if tags:
            clients = []
            for client in self._clients:
                for tag in tags:
                    if client.is_tag(tag):
                        clients.append(client)
                        break
        else:
            clients = self._clients
        for client in clients:
            if not client.is_active():
                self._clients.remove(client)
            yield from client.send(message)


class WebSocketServer():
    clients = Clients()
    server_handler, broker_handler = None, None

    def __init__(self, server_handler, broker_handler):
        self.server_handler = server_handler
        self.broker_handler = broker_handler

    def run(self):
        start_server = websockets.serve(
            partial(self.server_handler, self),
            config.WS_HOST, config.WS_PORT
        )
        asyncio.async(self.broker_handler(self))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()

    def receiver(self, client, message):
        try:
            msg = json.loads(message)
        except ValueError:
            msg = {'message': message}
        if msg.get('tags'):
            client.init_tags(msg['tags'])


@asyncio.coroutine
def server_handler(server, websocket, path):
    client = Client(websocket)
    server.clients.add_client(client)
    while True:
        try:
            message = yield from websocket.recv()
            if message == 'ping':
                logger.debug('ping from {}'.format(client.name()))
            else:
                logger.info('received: {}'.format(message))
            if message is None:
                break
            yield server.receiver(client, message)
        except Exception as exc:
            logger.error('\n'.join(traceback.format_tb(sys.exc_info()[2])))


@asyncio.coroutine
def redis_handler(server):
    connection = yield from asyncio_redis.Connection.create(
        host=config.CACHE_HOST,
        port=config.CACHE_PORT,
    )
    subscriber = yield from connection.start_subscribe()
    yield from subscriber.subscribe([config.WS_CHANNEL])
    while True:
        try:
            pub = yield from subscriber.next_published()
            message = json.loads(pub.value)
            logger.info('send: {} - "{}"'.format(', '.join(message['tags']) if 'tags' in message else 'ALL', message['message']))
            tags = message['tags'] if 'tags' in message else []
            yield from server.clients.send(message['message'], tags)
        except Exception as exc:
            logger.error('\n'.join(traceback.format_tb(sys.exc_info()[2])))


if __name__ == '__main__':
    WebSocketServer(server_handler, redis_handler).run()
