from datetime import datetime

import peewee

import config
import consts
import errors
from helpers import encrypt_password, generate_token
from cache import set_cache, get_cache, delete_cache


class BaseModel(peewee.Model):
    class Meta:
        database = config.DB


class User(BaseModel):
    pk = peewee.PrimaryKeyField()
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    email = peewee.CharField(null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    date_verified = peewee.DateTimeField(null=True)
    date_verification_token = peewee.DateTimeField(null=True)

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

    @classmethod
    def verify_email(cls, token):
        user_id = get_cache(token)
        if user_id:
            user = cls.get(pk=user_id)
            user.verify()
            delete_cache(token)
            return user
        return False

    def get_verification(self):
        if self.verified:
            raise errors.VerifiedError
        if not self.email:
            raise AttributeError('your email is not defined')
        if self.date_verification_token:
            seconds = (datetime.now() - self.date_verification_token).total_seconds()
            if seconds < config.VERIFICATION_PERIOD:
                raise errors.VerificationRequestError(config.VERIFICATION_PERIOD - int(seconds))
        token = generate_token()
        set_cache(token, self.pk, config.VERIFICATION_TIME)
        self.date_verification_token = datetime.now()
        self.save()
        return token

    def verify(self):
        self.date_verified = datetime.now()
        self.save()

    @property
    def verified(self):
        return bool(self.date_verified)


class Game(BaseModel):
    pk = peewee.PrimaryKeyField()
    player_white = peewee.ForeignKeyField(User, related_name='games_white', null=True)
    player_black = peewee.ForeignKeyField(User, related_name='games_black', null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    date_end = peewee.DateTimeField(null=True)
    state = peewee.CharField(null=True)
    date_state = peewee.DateTimeField(default=datetime.now)
    next_color = peewee.IntegerField(default=consts.WHITE)

    def add_move(self, figure, move):
        num = self.moves.select().count() + 1
        return Move.create(game=self, number=num, figure=figure, move=move)

    def save_state(self, state, next_color):
        self.state = state
        self.next_color = next_color
        self.date_state = datetime.now()
        self.save()


class Move(BaseModel):
    pk = peewee.PrimaryKeyField()
    game = peewee.ForeignKeyField(Game, related_name='moves')
    number = peewee.IntegerField()
    figure = peewee.FixedCharField(max_length=1)
    move = peewee.CharField(max_length=5)
    date_created = peewee.DateTimeField(default=datetime.now)


if __name__ == '__main__':
    config.DB.connect()
    config.DB.create_tables([User])
    config.DB.create_tables([Game])
    config.DB.create_tables([Move])
