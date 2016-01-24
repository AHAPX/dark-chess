import json

from flask import Flask

from tests.base import TestCaseBase
import serializers
from engine import Board
from consts import WHITE, BLACK, KING


class TestSerializer(TestCaseBase):

    def setUp(self):
        self.app = Flask(__name__)

    def test_base(self):
        with self.app.test_request_context():
            # success
            resp = serializers.BaseSerializer({'data': 'test'}).to_json()
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            self.assertEqual(data['data'], 'test')
            # error
            resp = serializers.BaseSerializer('data').to_json()
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(data['rc'])
            self.assertEqual(data['error'], 'system error')
            # succes with rc = False
            resp = serializers.BaseSerializer({'rc': False, 'data': 'test'}).to_json()
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertFalse(data['rc'])
            self.assertEqual(data['data'], 'test')

    def test_figure(self):
        with self.app.test_request_context():
            figure = Board('Ke1').getFigure(WHITE, KING)
            resp = serializers.FigureSerializer(figure).to_json()
            data = json.loads(resp.data)
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
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': {}, 'b3': {}, 'c3': {}, 'c4': {}, 'd2': {}, 'd3': {},
                'd4': {}, 'd5': {}, 'd6': {}, 'd7': {}, 'd8': {}, 'e2': {},
                'f3': {}, 'g4': {}, 'h5': {}, 'g8': {}, 'g4': {}, 'f5': {},
                'f7': {}, 'a1': {}, 'b1': {}, 'c1': {}, 'e1': {}, 'f1': {},
                'g1': {}, 'h1': {},
                'c2': {'kind': 'pawn', 'color': 'white', 'position': 'c2'},
                'd1': {'kind': 'queen', 'color': 'white', 'position': 'd1'},
                'h6': {'kind': 'knight', 'color': 'white', 'position': 'h6'},
            }
            self.compare_dicts(data, expect)

    def test_board_2(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8')
            resp = serializers.BoardSerializer(board, BLACK).to_json()
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(data['rc'])
            expect = {
                'rc': {}, 'd8': {}, 'd7': {}, 'e7': {}, 'f7': {}, 'f8': {},
                'e8': {'kind': 'king', 'color': 'black', 'position': 'e8'},
            }
            self.compare_dicts(data, expect)



