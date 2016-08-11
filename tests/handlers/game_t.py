from tests.base import TestCaseWeb
from cache import get_cache
from models import Game, User
from helpers import get_prefix, get_queue_name
from consts import TYPES, TYPE_NOLIMIT, BLACK, WHITE


class TestHandlerGame(TestCaseWeb):
    url_prefix = '/v1/game/'

    def new_game(self, game_type=None, game_limit=None):
        game_data = {
            'type': game_type,
            'limit': game_limit,
        }
        resp = self.client.post(self.url('new'), data=game_data)
        token1 = self.load_data(resp)['game']
        resp = self.client.post(self.url('new'), data=game_data)
        token2 = self.load_data(resp)['game']
        return token1, token2

    def test_types(self):
        resp = self.client.get(self.url('types'))
        data = self.load_data(resp)
        self.assertEqual(len(data['types']), len(TYPES.items()))
        index = 0
        for key in TYPES.keys():
            self.assertEqual(len(data['types'][index]['periods']), len(TYPES[key]['periods']))
            index += 1

    def test_new_game_1(self):
        # wrong method
        resp = self.client.get(self.url('new'))
        self.assertEqual(resp.status_code, 405)
        # validator create error
        game_data = {'type': 'err_type'}
        resp = self.client.post(self.url('new'), data=game_data)
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)
        # validation field error
        game_data = {'type': 'slow', 'limit': 'err_limit'}
        resp = self.client.post(self.url('new'), data=game_data)
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_new_game_2(self):
        # two requests with the same type and limit, start game
        game_data = {'type': 'slow', 'limit': '1d'}
        # send first request
        resp = self.client.post(self.url('new'), data=game_data)
        data = self.load_data(resp)
        user1_token = data['game']
        expect = {'rc': True, 'game': {}}
        self.assertComprateDicts(data, expect)
        # send second request
        resp = self.client.post(self.url('new'), data=game_data)
        data = self.load_data(resp)
        user2_token = data['game']
        expect = {
            'rc': True, 'board': {}, 'time_left': {}, 'enemy_time_left': {},
            'started_at': {}, 'ended_at': None, 'game': {}, 'next_turn': 'white'
        }
        self.assertComprateDicts(data, expect)
        # check game and cache
        game = Game.get()
        self.assertIsNone(game.player_white)
        self.assertIsNone(game.player_black)
        self.assertEqual(get_cache(user1_token), (game.pk, WHITE, user2_token))
        self.assertEqual(get_cache(user2_token), (game.pk, BLACK, user1_token))

    def test_new_game_3(self):
        # case 2 with login
        self.login(*self.add_user('user1', 'password', None))
        self.client.post(self.url('new'), data={})
        self.login(*self.add_user('user2', 'password', None))
        self.client.post(self.url('new'), data={})
        game = Game.get()
        self.assertIsInstance(game.player_white, User)
        self.assertIsInstance(game.player_black, User)

    def test_new_game_4(self):
        # two requests: first has limit, second not, start game
        game_data = {'type': 'slow', 'limit': '1d'}
        self.client.post(self.url('new'), data=game_data)
        resp = self.client.post(self.url('new'), data={'type': 'slow'})
        data = self.load_data(resp)
        expect = {
            'rc': True, 'board': {}, 'time_left': {}, 'enemy_time_left': {},
            'started_at': {}, 'ended_at': None, 'game': {}, 'next_turn': 'white'
        }
        self.assertComprateDicts(data, expect)

    def test_new_game_5(self):
        # two requests: second has limit, first not, start game
        self.client.post(self.url('new'), data={'type': 'slow'})
        game_data = {'type': 'slow', 'limit': '1d'}
        resp = self.client.post(self.url('new'), data=game_data)
        data = self.load_data(resp)
        expect = {
            'rc': True, 'board': {}, 'time_left': {}, 'enemy_time_left': {},
            'started_at': {}, 'ended_at': None, 'game': {}, 'next_turn': 'white'
        }
        self.assertComprateDicts(data, expect)

    def test_new_game_6(self):
        # two requests without limit, not start game
        self.client.post(self.url('new'), data={'type': 'slow'})
        resp = self.client.post(self.url('new'), data={'type': 'slow'})
        data = self.load_data(resp)
        expect = {'rc': True, 'game': {}}
        self.assertComprateDicts(data, expect)

    def test_new_game_7(self):
        # one user starts game twice, only last should stay
        name = get_queue_name(get_prefix(TYPE_NOLIMIT))
        self.login(*self.add_user('user1', 'password', None))
        resp = self.client.post(self.url('new'), data={})
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        token1 = data['game']
        self.assertIn(token1, get_cache(name).decode())
        resp = self.client.post(self.url('new'), data={})
        data = self.load_data(resp)
        self.assertTrue(data['rc'])
        token2 = data['game']
        self.assertNotIn(token1, get_cache(name).decode())
        self.assertIn(token2, get_cache(name).decode())

    def test_invite_1(self):
        resp = self.client.post(self.url('invite'), data={'type': 'slow'})
        self.assertFalse(self.load_data(resp)['rc'])

    def test_invite_2(self):
        # create invitation
        resp = self.client.post(self.url('invite'), data={'type': 'no limit'})
        data = self.load_data(resp)
        expect = {'rc': True, 'game': {}, 'invite': {}}
        self.assertComprateDicts(data, expect)
        token = data['invite']
        # start game with invitation token
        resp = self.client.get(self.url('invite/{}'.format(token)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'board': {}, 'time_left': {}, 'enemy_time_left': {},
            'started_at': {}, 'ended_at': None, 'game': {}, 'next_turn': 'white'
        }
        self.assertComprateDicts(data, expect)

    def test_invite_3(self):
        resp = self.client.get(self.url('invite/token'), data={'type': 'slow'})
        self.assertFalse(self.load_data(resp)['rc'])

    def test_active(self):
        # create user1 and invite
        self.login(*self.add_user('user1', 'password', None))
        resp = self.client.post(self.url('invite'), data={'type': 'no limit'})
        data = self.load_data(resp)
        game1_w = data['game']
        # create user2, accept invite and invite again
        self.login(*self.add_user('user2', 'password', None))
        resp = self.client.get(self.url('invite/{}'.format(data['invite'])))
        game1_b = self.load_data(resp)['game']
        resp = self.client.post(self.url('invite'), data={'type': 'no limit'})
        data = self.load_data(resp)
        game2_w = data['game']
        # check games of user2
        resp = self.client.get(self.url('active'))
        self.assertEqual(self.load_data(resp), {'rc': True, 'games': [game1_b]})
        # login as user1, accept invite and check games
        self.login('user1', 'password')
        resp = self.client.get(self.url('invite/{}'.format(data['invite'])))
        game2_b = self.load_data(resp)['game']
        resp = self.client.get(self.url('active'))
        self.assertEqual(self.load_data(resp), {'rc': True, 'games': [game1_w, game2_b]})

    def test_game_info(self):
        user_token1, user_token2 = self.new_game()
        # test first token
        resp = self.client.get(self.url('{}/info'.format(user_token1)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': None, 'board': {},
            'time_left': {}, 'enemy_time_left': {}, 'next_turn': 'white',
        }
        self.assertComprateDicts(data, expect)
        # test second token
        resp = self.client.get(self.url('{}/info'.format(user_token2)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': None, 'board': {},
            'time_left': {}, 'enemy_time_left': {}, 'next_turn': 'white',
        }
        self.assertComprateDicts(data, expect)

    def test_game_move_1(self):
        user_token1, user_token2 = self.new_game()
        # wrong method
        resp = self.client.get(self.url('token/move'))
        self.assertEqual(resp.status_code, 405)
        # validator create error
        resp = self.client.post(self.url('{}/move'.format(user_token1)), data={})
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)
        # validation field error
        move_data = {'move': 'e0-e1'}
        resp = self.client.post(self.url('{}/move'.format(user_token2)), data=move_data)
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_game_move_2(self):
        user_token1, user_token2 = self.new_game()
        move_data = {'move': 'e2-e4'}
        resp = self.client.post(self.url('{}/move'.format(user_token1)), data=move_data)
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': None, 'board': {},
            'time_left': {}, 'enemy_time_left': {}, 'next_turn': 'black',
        }
        self.assertComprateDicts(data, expect)

    def test_draw_accept(self):
        user_token1, user_token2 = self.new_game()
        # draw request and accept after, game is over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token2)))
        data = self.load_data(resp)
        expect = {'rc': True, 'message': {}}
        self.assertComprateDicts(data, expect)

    def test_draw_refuse_1(self):
        user_token1, user_token2 = self.new_game()
        # draw request and refuse after by second player, game is not over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        resp = self.client.get(self.url('{}/draw/refuse'.format(user_token2)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        # draw request from second player, game is not over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token2)))
        self.assertEqual(self.load_data(resp), {'rc': True})

    def test_draw_refuse_2(self):
        user_token1, user_token2 = self.new_game()
        # draw request and refuse after by first player, game is not over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        resp = self.client.get(self.url('{}/draw/refuse'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        # draw request from second player, game is not over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token2)))
        self.assertEqual(self.load_data(resp), {'rc': True})

    def test_resign(self):
        user_token1, user_token2 = self.new_game()
        # resign game
        resp = self.client.get(self.url('{}/resign'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        # try to resign ended game
        resp = self.client.get(self.url('{}/resign'.format(user_token2)))
        data = self.load_data(resp)
        self.assertFalse(data['rc'])
        self.assertIn('error', data)

    def test_moves(self):
        user_token1, user_token2 = self.new_game()
        move1, move2 = 'e2-e4', 'e7-e5'
        # do moves
        self.client.post(self.url('{}/move'.format(user_token1)), data={'move': move1})
        self.client.post(self.url('{}/move'.format(user_token2)), data={'move': move2})
        # check moves
        resp = self.client.get(self.url('{}/moves'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True, 'moves': [move1]})
        resp = self.client.get(self.url('{}/moves'.format(user_token2)))
        self.assertEqual(self.load_data(resp), {'rc': True, 'moves': [move2]})
        # end game and check moves again
        self.client.get(self.url('{}/resign'.format(user_token1)))
        resp = self.client.get(self.url('{}/moves'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True, 'moves': [move1, move2]})
        resp = self.client.get(self.url('{}/moves'.format(user_token2)))
        self.assertEqual(self.load_data(resp), {'rc': True, 'moves': [move1, move2]})
