import json
from datetime import datetime

from flask import Flask

import config
from tests.base import TestCaseBase
import serializers
from engine import Board
from consts import UNKNOWN, WHITE, BLACK, KING
from models import User, Move, ChatMessage


class TestSerializer(TestCaseBase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_base(self):
        with self.app.test_request_context():
            # success
            resp = serializers.BaseSerializer({'data': 'test'}).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            self.assertEqual(data['data'], 'test')
            # error
            with self.assertLogs('serializers', level='ERROR'):
                resp = serializers.BaseSerializer('data').to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(data['rc'])
            self.assertEqual(data['error'], 'system error')
            # succes with rc = False
            resp = serializers.BaseSerializer({'rc': False, 'data': 'test'}).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(data['rc'])
            self.assertEqual(data['data'], 'test')

    def test_figure(self):
        with self.app.test_request_context():
            figure = Board('Ke1').getFigure(WHITE, KING)
            resp = serializers.FigureSerializer(figure).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            self.assertEqual(data['kind'], 'king')
            self.assertEqual(data['color'], 'white')
            self.assertEqual(data['position'], 'e1')
            self.assertEqual(sorted(data['moves']), sorted(['d1', 'd2', 'e2', 'f2', 'f1']))

    def test_board_1(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8', 'pPnNbBrRqQ')
            resp = serializers.BoardSerializer(board, WHITE).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': True, 'b3': {}, 'c3': {}, 'c4': {}, 'd2': {}, 'd3': {},
                'd4': {}, 'd5': {}, 'd6': {}, 'd7': {}, 'd8': {}, 'e2': {},
                'f3': {}, 'g4': {}, 'h5': {}, 'g8': {}, 'g4': {}, 'f5': {},
                'f7': {}, 'a1': {}, 'b1': {}, 'c1': {}, 'e1': {}, 'f1': {},
                'g1': {}, 'h1': {},
                'c2': {'kind': 'pawn', 'color': 'white', 'position': 'c2'},
                'd1': {'kind': 'queen', 'color': 'white', 'position': 'd1'},
                'h6': {'kind': 'knight', 'color': 'white', 'position': 'h6'},
                'cuts': [
                    {'color': 'black', 'kind': 'pawn'},
                    {'color': 'white', 'kind': 'pawn'},
                    {'color': 'black', 'kind': 'knight'},
                    {'color': 'white', 'kind': 'knight'},
                    {'color': 'black', 'kind': 'bishop'},
                    {'color': 'white', 'kind': 'bishop'},
                    {'color': 'black', 'kind': 'rook'},
                    {'color': 'white', 'kind': 'rook'},
                    {'color': 'black', 'kind': 'queen'},
                    {'color': 'white', 'kind': 'queen'},
                ],
            }
            self.assertComprateDicts(data, expect)

    def test_board_2(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8')
            resp = serializers.BoardSerializer(board, BLACK).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': True, 'd8': {}, 'd7': {}, 'e7': {}, 'f7': {}, 'f8': {},
                'e8': {'kind': 'king', 'color': 'black', 'position': 'e8'},
                'cuts': [],
            }
            self.assertComprateDicts(data, expect)

    def test_board_3(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8', 'K')
            resp = serializers.BoardSerializer(board, UNKNOWN).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': True, 'a1': {}, 'a2': {}, 'a3': {}, 'a4': {}, 'a5': {},
                'a6': {}, 'a7': {}, 'a8': {}, 'b1': {}, 'b2': {}, 'b3': {},
                'b4': {}, 'b5': {}, 'b6': {}, 'b7': {}, 'b8': {}, 'c1': {},
                'c3': {}, 'c4': {}, 'c5': {}, 'c6': {}, 'c7': {}, 'c8': {},
                'd2': {}, 'd3': {}, 'd4': {}, 'd5': {}, 'd6': {}, 'd7': {},
                'd8': {}, 'e1': {}, 'e2': {}, 'e3': {}, 'e4': {}, 'e5': {},
                'e6': {}, 'e7': {}, 'f1': {}, 'f2': {}, 'f3': {}, 'f4': {},
                'f5': {}, 'f6': {}, 'f7': {}, 'f8': {}, 'g1': {}, 'g2': {},
                'g3': {}, 'g4': {}, 'g5': {}, 'g6': {}, 'g7': {}, 'g8': {},
                'h1': {}, 'h2': {}, 'h3': {}, 'h4': {}, 'h5': {}, 'h7': {},
                'h8': {},
                'c2': {'kind': 'pawn', 'color': 'white', 'position': 'c2'},
                'd1': {'kind': 'queen', 'color': 'white', 'position': 'd1'},
                'e8': {'kind': 'king', 'color': 'black', 'position': 'e8'},
                'h6': {'kind': 'knight', 'color': 'white', 'position': 'h6'},
                'cuts': [{'color': 'white', 'kind': 'king'}],
            }
            self.assertComprateDicts(data, expect)

    def test_move(self):
        with self.app.test_request_context():
            cases = [
                (Move(figure='N', move='b2-c3'), 'Nb2-c3'),
                (Move(figure='k', move='e8-e7'), 'Ke8-e7'),
                (Move(figure='K', move='0-0-0'), '0-0-0'),
                (Move(figure='P', move='e2-e4'), 'e2-e4'),
            ]
            for move, expect in cases:
                self.assertEqual(serializers.MoveSerializer(move).calc(), expect)

    def test_message_1(self):
        with self.app.test_request_context():
            dt = datetime.now()
            message = ChatMessage(text='hello', date_created=dt)
            expect = {
                'user': 'anonymous',
                'text': 'hello',
                'created_at': dt.isoformat(),
            }
            self.assertEqual(serializers.MessageSerializer(message).calc(), expect)

    def test_message_2(self):
        with self.app.test_request_context():
            dt = datetime.now()
            config.SITE_URL = 'http://localhost'
            user = User(username='user1', password='passwd')
            message = ChatMessage(text='http://localhost/someurl', date_created=dt, user=user)
            expect = {
                'user': 'user1',
                'text': '/someurl',
                'link': 'http://localhost/someurl',
                'created_at': dt.isoformat(),
            }
            self.assertEqual(serializers.MessageSerializer(message).calc(), expect)
