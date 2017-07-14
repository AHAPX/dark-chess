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
            data = serializers.BaseSerializer({'data': 'test'}).calc()
            self.assertEqual(data['data'], 'test')

    def test_figure(self):
        with self.app.test_request_context():
            figure = Board('Ke1').getFigure(WHITE, KING)
            data = serializers.FigureSerializer(figure).calc()
            self.assertEqual(data['kind'], 'king')
            self.assertEqual(data['color'], 'white')
            self.assertEqual(data['position'], 'e1')
            self.assertEqual(sorted(data['moves']), sorted(['d1', 'd2', 'e2', 'f2', 'f1']))

    def test_board_1(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8', 'pPnNbBrRqQ')
            data = serializers.BoardSerializer(board, WHITE).calc()
            expect = {
                'b3': {}, 'c3': {}, 'c4': {}, 'd2': {}, 'd3': {},
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
            self.assertCompareDicts(data, expect)

    def test_board_2(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8')
            data = serializers.BoardSerializer(board, BLACK).calc()
            expect = {
                'd8': {}, 'd7': {}, 'e7': {}, 'f7': {}, 'f8': {},
                'e8': {'kind': 'king', 'color': 'black', 'position': 'e8'},
                'cuts': [],
            }
            self.assertCompareDicts(data, expect)

    def test_board_3(self):
        with self.app.test_request_context():
            board = Board('Pc2,Qd1,Nh6,ke8', 'K')
            data = serializers.BoardSerializer(board, UNKNOWN).calc()
            expect = {
                'a1': {}, 'a2': {}, 'a3': {}, 'a4': {}, 'a5': {},
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
            self.assertCompareDicts(data, expect)

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
