import time
from datetime import datetime, timedelta

import config
import errors
from tests.base import TestCaseDB
from consts import WHITE, BLACK
from models import User, Game, Move
from cache import get_cache


class TestModels(TestCaseDB):

    def test_User(self):
        # add user and check fields
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
        game = Game.create(player_white='123', player_black='456', state='Ke1,ke8')
        self.assertTrue(abs((game.date_created - game.date_state).total_seconds()) < 1)
        self.assertEqual(game.next_color, WHITE)
        self.assertEqual(Game.select().count(), 1)
        self.assertEqual(Move.select().count(), 0)
        game.add_move('K', 'e1-e2')
        self.assertEqual(Move.select().count(), 1)
        time.sleep(1)
        game.save_state('Ke2,k28', BLACK)
        game = Game.get(pk=game.pk)
        self.assertEqual(game.next_color, BLACK)
        self.assertEqual(game.state, 'Ke2,k28')
        self.assertTrue((game.date_state - game.date_created).total_seconds() > 1)

    def test_verification(self):
        user = User.add('user1', 'passwd')
        self.assertFalse(user.verified)
        self.assertFalse(User.verify_email('qwerty'))
        with self.assertRaises(AttributeError):
            user.get_verification()
        user.email = 'user1@fakemail.net'
        user.save()
        token = user.get_verification()
        with self.assertRaises(errors.VerificationRequestError):
            user.get_verification()
        user.date_verification_token = datetime.now() - timedelta(seconds=config.VERIFICATION_PERIOD + 1)
        user.save()
        token = user.get_verification()
        self.assertEqual(User.verify_email(token).pk, user.pk)
        user = User.get(pk=user.pk)
        self.assertTrue(user.verified)
        with self.assertRaises(errors.VerifiedError):
            user.get_verification()
