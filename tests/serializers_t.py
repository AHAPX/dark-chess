import json

from flask import Flask

from tests.base import TestCaseBase
import serializers
from engine import Board
from consts import UNKNOWN, WHITE, BLACK, KING
from models import Move


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
            board = Board('Pc2,Qd1,Nh6,ke8')
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
            }
            self.assertComprateDicts(data, expect)

    def test_board_3(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8')
            resp = serializers.BoardSerializer(board, UNKNOWN).to_json()
            data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': True, 'b3': {}, 'c3': {}, 'c4': {}, 'd2': {}, 'd3': {},
                'd4': {}, 'd5': {}, 'd6': {}, 'd7': {}, 'd8': {}, 'e2': {},
                'e7': {}, 'f3': {}, 'g4': {}, 'h5': {}, 'g8': {}, 'g4': {},
                'f5': {}, 'f7': {}, 'f8': {}, 'a1': {}, 'b1': {}, 'c1': {},
                'e1': {}, 'f1': {}, 'g1': {}, 'h1': {},
                'c2': {'kind': 'pawn', 'color': 'white', 'position': 'c2'},
                'd1': {'kind': 'queen', 'color': 'white', 'position': 'd1'},
                'e8': {'kind': 'king', 'color': 'black', 'position': 'e8'},
                'h6': {'kind': 'knight', 'color': 'white', 'position': 'h6'},
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
