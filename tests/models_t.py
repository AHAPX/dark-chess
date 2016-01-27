import time
from datetime import datetime, timedelta

import config
import errors
from tests.base import TestCaseDB
from consts import WHITE, BLACK, TYPE_SLOW, TYPE_FAST
from models import User, Game, Move
from cache import get_cache


class TestModels(TestCaseDB):

    def test_User(self):
        # add user and check it
        user = User.add('user1', 'passwd', 'user1@fakemail.net')
        self.assertEqual(User.select().count(), 1)
        self.assertEqual(user.username, 'user1')
        self.assertEqual(user.email, 'user1@fakemail.net')
        self.assertEqual(user.date_verified, None)
        # verification
        self.assertFalse(user.verified)
        user.verify()
        self.assertTrue(user.verified)
        # authentication
        self.assertFalse(User.authenticate('user1', 'passw'))
        token = User.authenticate('user1', 'passwd')
        self.assertEqual(User.get(pk=get_cache(token)).password, str(user.password))

    def test_Game_and_Move(self):
        # add game and check it
        game = Game.create(player_white='123', player_black='456', state='Ke1,ke8')
        self.assertTrue(abs((game.date_created - game.date_state).total_seconds()) < 1)
        self.assertEqual(game.next_color, WHITE)
        self.assertEqual(Game.select().count(), 1)
        self.assertEqual(Move.select().count(), 0)
        self.assertFalse(game.ended)
        # wait a second
        time.sleep(1)
        # add move and check
        game.add_move('K', 'e1-e2', 'Ke2,ke8')
        self.assertEqual(Move.select().count(), 1)
        # reload game
        game = Game.get(pk=game.pk)
        self.assertEqual(game.next_color, BLACK)
        self.assertEqual(game.state, 'Ke2,ke8')
        self.assertTrue((game.date_state - game.date_created).total_seconds() > 1)
        self.assertEqual(round(game.moves.get().time_move), 1)
        self.assertFalse(game.ended)
        # add move with ending game
        game.add_move('k', 'e8-e7', 'Ke2,ke7', True)
        self.assertTrue(game.ended)

    def test_verification(self):
        # add user and check it
        user = User.add('user1', 'passwd')
        self.assertFalse(user.verified)
        self.assertFalse(User.verify_email('qwerty'))
        # try to verificate without email
        with self.assertRaises(AttributeError):
            user.get_verification()
        # add email
        user.email = 'user1@fakemail.net'
        user.save()
        # get verification success
        token = user.get_verification()
        # try to verificate again
        with self.assertRaises(errors.VerificationRequestError):
            user.get_verification()
        user.date_verification_token = datetime.now() - timedelta(seconds=config.VERIFICATION_PERIOD + 1)
        user.save()
        # get verification success
        token = user.get_verification()
        self.assertEqual(User.verify_email(token).pk, user.pk)
        # reload user
        user = User.get(pk=user.pk)
        self.assertTrue(user.verified)
        # try to verificate verificated user
        with self.assertRaises(errors.VerifiedError):
            user.get_verification()

    def test_game_over_1(self):
        # add game and check it
        game = Game.create(player_white='123', player_black='456', state='Ke1,ke8')
        self.assertFalse(game.ended)
        self.assertIsNone(game.end_reason)
        self.assertIsNone(game.date_end)
        # game over with saving
        game.game_over(1)
        self.assertTrue(game.ended)
        self.assertEqual(game.end_reason, 1)
        self.assertIsNotNone(game.date_end)
        # reload game
        game = Game.get(pk=game.pk)
        self.assertTrue(game.ended)
        self.assertEqual(game.end_reason, 1)
        self.assertIsNotNone(game.date_end)

    def test_game_over_2(self):
        # add game and check it
        game = Game.create(player_white='123', player_black='456', state='Ke1,ke8')
        self.assertFalse(game.ended)
        self.assertIsNone(game.end_reason)
        self.assertIsNone(game.date_end)
        # game over without saving
        game.game_over(1, datetime(2015, 1, 27, 12, 0, 0), False)
        self.assertTrue(game.ended)
        self.assertEqual(game.end_reason, 1)
        self.assertEqual(game.date_end, datetime(2015, 1, 27, 12, 0, 0))
        # reload game
        game = Game.get(pk=game.pk)
        self.assertFalse(game.ended)
        self.assertIsNone(game.end_reason)
        self.assertIsNone(game.date_end)

    def test_time_left_1(self):
        # add game, moves and check them
        game = Game.create(
            player_white='123', player_black='456', state='Ke1,ke8',
            type_game=TYPE_FAST, time_limit=20
        )
        Move.create(game=game, number=1, figure='K', move='e1-e2', time_move=9, color=WHITE)
        Move.create(game=game, number=2, figure='k', move='e8-e7', time_move=3, color=BLACK)
        Move.create(game=game, number=3, figure='K', move='e2-e3', time_move=5, color=WHITE)
        Move.create(game=game, number=4, figure='k', move='e7-e8', time_move=6, color=BLACK)
        self.assertFalse(game.ended)
        self.assertEqual(round(game.time_left(WHITE)), 6)
        self.assertEqual(round(game.time_left(BLACK)), 11)
        self.assertFalse(game.is_time_over())
        # shift date_state in limit
        game.date_state = datetime.now() - timedelta(seconds=3)
        self.assertEqual(round(game.time_left(WHITE)), 3)
        self.assertEqual(round(game.time_left(BLACK)), 11)
        self.assertFalse(game.is_time_over())
        # shift date_state out limit
        game.date_state = datetime.now() - timedelta(seconds=10)
        self.assertTrue(game.is_time_over())
        self.assertTrue(game.ended)
        self.assertFalse(game.is_time_over())

    def test_time_left_2(self):
        # add game, moves and check them
        game = Game.create(
            player_white='123', player_black='456', state='Ke1,ke8',
            type_game=TYPE_SLOW, time_limit=10
        )
        Move.create(game=game, number=1, figure='K', move='e1-e2', time_move=9, color=WHITE)
        Move.create(game=game, number=2, figure='k', move='e8-e7', time_move=3, color=BLACK)
        Move.create(game=game, number=3, figure='K', move='e2-e3', time_move=5, color=WHITE)
        Move.create(game=game, number=4, figure='k', move='e7-e8', time_move=6, color=BLACK)
        self.assertFalse(game.ended)
        self.assertEqual(round(game.time_left(WHITE)), 10)
        self.assertEqual(round(game.time_left(BLACK)), 10)
        # shift date_state in limit
        self.assertFalse(game.is_time_over())
        game.date_state = datetime.now() - timedelta(seconds=3)
        self.assertEqual(round(game.time_left(WHITE)), 7)
        self.assertEqual(round(game.time_left(BLACK)), 10)
        self.assertFalse(game.is_time_over())
        # shift date_state out limit
        game.date_state = datetime.now() - timedelta(seconds=10)
        self.assertTrue(game.is_time_over())
        self.assertTrue(game.ended)
        self.assertFalse(game.is_time_over())

    def test_time_left_3(self):
        # add game, moves and check them
        game = Game.create(
            player_white='123', player_black='456', state='Ke1,ke8',
            time_limit=10
        )
        Move.create(game=game, number=1, figure='K', move='e1-e2', time_move=9, color=WHITE)
        Move.create(game=game, number=2, figure='k', move='e8-e7', time_move=3, color=BLACK)
        Move.create(game=game, number=3, figure='K', move='e2-e3', time_move=5, color=WHITE)
        Move.create(game=game, number=4, figure='k', move='e7-e8', time_move=6, color=BLACK)
        self.assertFalse(game.ended)
        self.assertIsNone(game.time_left(WHITE))
        self.assertIsNone(game.time_left(BLACK))
        self.assertFalse(game.is_time_over())
        # shift date_state out limit
        game.date_state = datetime.now() - timedelta(days=1000)
        self.assertIsNone(game.time_left(WHITE))
        self.assertIsNone(game.time_left(BLACK))
        self.assertFalse(game.is_time_over())
