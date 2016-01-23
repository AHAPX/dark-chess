import unittest
import inspect
import sys

from playhouse.test_utils import test_database
from peewee import SqliteDatabase, Model

from models import User, Game, Move


test_db = SqliteDatabase(':memory:')


class TestCaseDB(unittest.TestCase):

    def run(self, result=None):
        model_classes = [
            m[1] for m in inspect.getmembers(sys.modules['models'], inspect.isclass)
            if issubclass(m[1], Model) and m[1] != Model
        ]
        with test_database(test_db, model_classes):
            super(TestCaseDB, self).run(result)
