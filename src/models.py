from datetime import datetime, timedelta

import peewee

import config
import consts
import errors
from helpers import encrypt_password, generate_token, invert_color
from cache import set_cache, get_cache, delete_cache


class BaseModel(peewee.Model):
    class Meta:
        database = config.DB


class User(BaseModel):
    pk = peewee.PrimaryKeyField()
    username = peewee.CharField(unique=True)
    password = peewee.CharField()
    email = peewee.CharField(unique=True, null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    date_verified = peewee.DateTimeField(null=True)
    date_verification_token = peewee.DateTimeField(null=True)
    date_last_reset = peewee.DateTimeField(null=True)

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
    def get_by_token(cls, token):
        user_id = get_cache(token)
        if not user_id:
            return
        try:
            return cls.get(pk=user_id)
        except cls.DoesNotExist:
            return

    def set_password(self, password):
        self.password=encrypt_password(password)
        self.save()

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

    def get_reset(self):
        if not self.email:
            raise AttributeError('your email is not defined')
        if self.date_last_reset:
            seconds = (datetime.now() - self.date_last_reset).total_seconds()
            if seconds < config.RESET_PERIOD:
                raise errors.ResetRequestError(config.RESET_PERIOD - int(seconds))
        token = generate_token()
        set_cache(token, self.pk, config.RESET_TIME)
        self.date_last_reset = datetime.now()
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
    white = peewee.CharField()
    black = peewee.CharField()
    player_white = peewee.ForeignKeyField(User, related_name='games_white', null=True)
    player_black = peewee.ForeignKeyField(User, related_name='games_black', null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    date_end = peewee.DateTimeField(null=True)
    state = peewee.CharField(null=True)
    date_state = peewee.DateTimeField(default=datetime.now)
    next_color = peewee.IntegerField(default=consts.WHITE)
    type_game = peewee.IntegerField(default=consts.TYPE_NOLIMIT)
    time_limit = peewee.IntegerField(null=True)
    end_reason = peewee.IntegerField(null=True)
    winner = peewee.IntegerField(null=True)
    cut = peewee.CharField(default='')

    @classmethod
    def get_game(cls, token):
        game = cls.get((cls.white == token) | (cls.black == token))
        if game.white == token:
            game._loaded_by = consts.WHITE
        else:
            game._loaded_by = consts.BLACK
        return game

    def add_move(self, figure, move, state, end_reason=None):
        with config.DB.atomic():
            color = self.next_color
            num = self.moves.select().count() + 1
            time_move = (datetime.now() - self.date_state).total_seconds()
            self.state = state
            self.next_color = invert_color(color)
            self.date_state = datetime.now()
            if end_reason:
                self.game_over(end_reason, save=False, winner=color)
            self.save()
            return Move.create(
                game=self, number=num, figure=figure, move=move,
                time_move=time_move, color=color
            )

    def game_over(self, reason, date_end=None, save=True, winner=None):
        self.date_end = date_end or datetime.now()
        self.end_reason = reason
        self.winner = winner
        if save:
            self.save()

    @property
    def ended(self):
        return bool(self.date_end)

    def is_time_over(self):
        if self.ended:
            return False
        if self.type_game == consts.TYPE_SLOW:
            if (datetime.now() - self.date_state).total_seconds() > self.time_limit:
                self.game_over(
                    consts.END_TIME,
                    self.date_state + timedelta(seconds=self.time_limit),
                    winner=invert_color(self.next_color)
                )
                return True
        elif self.type_game == consts.TYPE_FAST:
            moves = self.moves.select(Move.time_move).where(Move.color == self.next_color)
            time_spent = sum([m.time_move for m in moves])
            if time_spent + (datetime.now() - self.date_state).total_seconds() > self.time_limit:
                self.game_over(
                    consts.END_TIME,
                    self.date_state + timedelta(seconds=self.time_limit - time_spent),
                    winner=invert_color(self.next_color)
                )
                return True
        return False

    def time_left(self, color):
        if self.ended:
            return None
        if self.type_game == consts.TYPE_SLOW:
            time_left = self.time_limit
            if self.next_color == color:
                time_left -= (datetime.now() - self.date_state).total_seconds()
            return time_left
        if self.type_game == consts.TYPE_FAST:
            moves = self.moves.select(Move.time_move).where(Move.color == color)
            time_spent = sum([m.time_move for m in moves])
            time_left = self.time_limit - time_spent
            if self.next_color == color:
                time_left -= (datetime.now() - self.date_state).total_seconds()
            return time_left

    def get_moves(self, color=None):
        moves = self.moves.select().order_by(Move.number)
        if color:
            moves = moves.where(Move.color == color)
        return moves

    def get_winner(self):
        if self.ended and self.winner:
            return consts.COLORS.get(self.winner)


class Move(BaseModel):
    pk = peewee.PrimaryKeyField()
    game = peewee.ForeignKeyField(Game, related_name='moves')
    number = peewee.IntegerField()
    figure = peewee.FixedCharField(max_length=1)
    move = peewee.CharField(max_length=5)
    date_created = peewee.DateTimeField(default=datetime.now)
    time_move = peewee.FloatField()
    color = peewee.IntegerField()


class Chat(BaseModel):
    pk = peewee.PrimaryKeyField()
    game = peewee.ForeignKeyField(Game, related_name='chats', on_delete='CASCADE')


class ChatMessage(BaseModel):
    pk = peewee.PrimaryKeyField()
    chat = peewee.ForeignKeyField(Chat, related_name='messages', null=True, on_delete='CASCADE')
    user = peewee.ForeignKeyField(User, related_name='messages', null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    text = peewee.CharField()


class GamePool(BaseModel):
    pk = peewee.PrimaryKeyField()
    player1 = peewee.CharField(null=True)
    player2 = peewee.CharField(null=True)
    user1 = peewee.ForeignKeyField(User, related_name='gamepools1', null=True)
    user2 = peewee.ForeignKeyField(User, related_name='gamepools2', null=True)
    date_created = peewee.DateTimeField(default=datetime.now)
    type_game = peewee.IntegerField(default=consts.TYPE_NOLIMIT)
    time_limit = peewee.IntegerField(null=True)
    is_started = peewee.BooleanField(default=False)
    is_lost = peewee.BooleanField(default=False)


if __name__ == '__main__':
    config.DB.connect()
    TABLES = [User, Game, Move, Chat, ChatMessage, GamePool]
    added = []
    for table in TABLES:
        if not table.table_exists():
            config.DB.create_tables([table])
            added.append(table.__name__)
    if added:
        print('Tables created: {}'.format(', '.join(added)))
    else:
        print('All tables already exist')
