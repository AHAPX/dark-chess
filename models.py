import datetime

import peewee

import config
from helpers import encrypt_password, generate_token
from cache import set_cache


class BaseModel(peewee.Model):
    class Meta:
        database = config.DB


class User(BaseModel):
    pk = peewee.PrimaryKeyField()
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    email = peewee.CharField(null=True)
    date_created = peewee.DateTimeField(default=datetime.datetime.now)
    verified = peewee.BooleanField(default=False)

    @classmethod
    def add(cls, username, password, email=None):
        return cls.create(username=username, password=encrypt_password(password), email=email)

    @classmethod
    def authenticate(cls, username, password):
        try:
            user = cls.get(username=username, password=encrypt_password(password))
        except cls.DoesNotExist:
            return False
        token = generate_token()
        set_cache(token, user.pk, config.SESSION_TIME)
        return token


class Game(BaseModel):
    pk = peewee.PrimaryKeyField()
    player_white = peewee.ForeignKeyField(User, related_name='games_white', null=True)
    player_black = peewee.ForeignKeyField(User, related_name='games_black', null=True)
    date_start = peewee.DateTimeField(default=datetime.datetime.now)
    date_end = peewee.DateTimeField(null=True)

    def add_move(self, figure, start, end):
        num = self.moves.select().count() + 1
        Move.create(game=self, number=num, figure=figure, start=start, end=end)


class Move(BaseModel):
    pk = peewee.PrimaryKeyField()
    game = peewee.ForeignKeyField(Game, related_name='moves')
    number = peewee.IntegerField()
    figure = peewee.FixedCharField(max_length=1)
    start = peewee.FixedCharField(max_length=2)
    end = peewee.FixedCharField(max_length=2)


if __name__ == '__main__':
    config.DB.connect()
    config.DB.create_tables([User])
    config.DB.create_tables([Game])
    config.DB.create_tables([Move])
