from tests.base import TestCaseWeb, SKIP
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
        resp = self.client.get(self.url('new'))
        data = self.load_data(resp)
        game_id = data['games'][0]['id']
        resp = self.client.post(self.url('new/{}'.format(game_id)))
        token2 = self.load_data(resp)['game']
        return token1, token2

    def test_types(self):
        resp = self.client.get(self.url('types'))
        data = self.load_data(resp)
        self.assertEqual(len(data['types']), len(TYPES.items()) - 1)
        index = 0
        for key in TYPES.keys():
            if key == TYPE_NOLIMIT:
                continue
            self.assertEqual(len(data['types'][index]['periods']), len(TYPES[key]['periods']))
            index += 1

    def test_new_game_0(self):
        expect1 = {
            'id': 2,
            'date_created': SKIP,
            'user': 'user1',
            'type': 'fast',
            'limit': 10 * 60,
        }
        expect2 = {
            'id': 1,
            'date_created': SKIP,
            'user': None,
            'type': 'slow',
            'limit': 24 * 60 * 60,
        }
        # send first request
        game_data = {'type': 'slow', 'limit': '1d'}
        resp = self.client.post(self.url('new'), data=game_data)
        # send second request
        self.login(*self.add_user('user1', 'password', None))
        game_data = {'type': 'fast', 'limit': '10m'}
        resp = self.client.post(self.url('new'), data=game_data)
        # check games
        resp = self.client.get(self.url('new'))
        data = self.load_data(resp)
        self.assertIn('games', data)
        self.assertEqual(len(data['games']), 1)
        self.assertCompareDicts(data['games'][0], expect2)
        # logout and check again
        self.logout()
        resp = self.client.get(self.url('new'))
        data = self.load_data(resp)
        self.assertIn('games', data)
        self.assertEqual(len(data['games']), 2)
        self.assertCompareDicts(data['games'][0], expect1)
        self.assertCompareDicts(data['games'][1], expect2)

    def test_new_game_1(self):
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

    def test_invite_1(self):
        # validation error
        resp = self.client.post(self.url('invite'), data={'type': 'slow'})
        self.assertFalse(self.load_data(resp)['rc'])

    def test_invite_2(self):
        # create invitation
        resp = self.client.post(self.url('invite'), data={'type': 'no limit'})
        data = self.load_data(resp)
        expect = {'rc': True, 'game': {}, 'invite': {}}
        self.assertCompareDicts(data, expect)
        token = data['invite']
        # start game with invitation token
        resp = self.client.get(self.url('invite/{}'.format(token)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'board': {}, 'time_left': {}, 'enemy_time_left': {},
            'started_at': {}, 'ended_at': None, 'game': {}, 'next_turn': 'white',
            'color': {}, 'opponent': {},
        }
        self.assertCompareDicts(data, expect)

    def test_invite_3(self):
        resp = self.client.get(self.url('invite/token'), data={'type': 'slow'})
        self.assertFalse(self.load_data(resp)['rc'])

    def test_games(self):
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
        resp = self.client.get(self.url('games'))
        expect = {
            'rc': True,
            'games': {'actives': [game1_b], 'ended': []},
        }
        self.assertEqual(self.load_data(resp), expect)
        # login as user1, accept invite and check games
        self.login('user1', 'password')
        resp = self.client.get(self.url('invite/{}'.format(data['invite'])))
        game2_b = self.load_data(resp)['game']
        resp = self.client.get(self.url('games'))
        expect = {
            'rc': True,
            'games': {'actives': [game1_w, game2_b], 'ended': []},
        }
        self.assertEqual(self.load_data(resp), expect)

    def test_game_info_1(self):
        # start game and check info for both colors
        user_token1, user_token2 = self.new_game()
        # test first token
        resp = self.client.get(self.url('{}/info'.format(user_token1)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': None, 'board': {},
            'time_left': {}, 'enemy_time_left': {}, 'next_turn': 'white',
            'color': {}, 'opponent': {},
        }
        self.assertCompareDicts(data, expect)
        # test second token
        resp = self.client.get(self.url('{}/info'.format(user_token2)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': None, 'board': {},
            'time_left': {}, 'enemy_time_left': {}, 'next_turn': 'white',
            'color': {}, 'opponent': {},
        }
        self.assertCompareDicts(data, expect)

    def test_game_info_2(self):
        # request new game and get info
        resp = self.client.post(self.url('new'), data={'type': 'no limit'})
        token = self.load_data(resp)['game']
        resp = self.client.get(self.url('{}/info'.format(token)))
        expect = {
            'rc': True, 'type': 'no limit', 'limit': None,
        }
        self.assertEqual(self.load_data(resp), expect)

    def test_game_info_3(self):
        # request invited game and get info
        resp = self.client.post(self.url('invite'), data={'type': 'no limit'})
        data = self.load_data(resp)
        token = data['game']
        invite_token = data['invite']
        resp = self.client.get(self.url('{}/info'.format(token)))
        expect = {
            'rc': True, 'type': 'no limit', 'limit': None,
            'invite': invite_token,
        }
        self.assertEqual(self.load_data(resp), expect)
        # shouldn't be info for invited token
        resp = self.client.get(self.url('{}/info'.format(invite_token)))
        self.assertFalse(self.load_data(resp)['rc'])

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
            'color': {}, 'opponent': {},
        }
        self.assertCompareDicts(data, expect)

    def test_draw_accept(self):
        user_token1, user_token2 = self.new_game()
        # draw request and accept after, game is over
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token1)))
        self.assertEqual(self.load_data(resp), {'rc': True})
        resp = self.client.get(self.url('{}/draw/accept'.format(user_token2)))
        data = self.load_data(resp)
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': {}, 'board': {},
            'color': {}, 'opponent': {}, 'winner': None,
        }
        self.assertCompareDicts(data, expect)

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
        expect = {
            'rc': True, 'started_at': {}, 'ended_at': {}, 'board': {},
            'color': {}, 'opponent': {}, 'winner': 'black',
        }
        self.assertCompareDicts(self.load_data(resp), expect)
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
