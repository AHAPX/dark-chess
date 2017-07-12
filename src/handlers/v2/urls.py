from handlers.v2 import main, auth, chat, game
from handlers.v2.base import BlueprintBase


bp_main = BlueprintBase('v2', __name__, url_prefix='/v2')
bp_main.urls([
    ('/', 'home', main.RestMain),
])


bp_auth = bp_main.addChild('auth', __name__, url_prefix='/auth')
bp_auth.urls([
    ('/register/', 'register', auth.RestRegister),
    ('/verification/', 'verification', auth.RestVerification),
    ('/verification/<token>/', 'verification_confirm', auth.RestVerificationConfirm),
    ('/reset/', 'reset', auth.RestReset),
    ('/recover/<token>/', 'recover', auth.RestRecover),
    ('/login/', 'login', auth.RestLogin),
    ('/logout/', 'logout', auth.RestLogout),
])

bp_chat = bp_main.addChild('chat', __name__, url_prefix='/chat')
bp_chat.urls([
    ('/messages/', 'messages', chat.RestMessages),
])

bp_game = bp_main.addChild('game', __name__, url_prefix='/game')
bp_game.urls([
    ('/types/', 'types', game.RestTypes),
    ('/new/', 'new', game.RestNewGame),
    ('/new/<game_id>/', 'accept', game.RestAcceptGame),
    ('/invite/', 'invite', game.RestNewInvite),
    ('/invite/<token>/', 'invited', game.RestAcceptInvite),
    ('/games/', 'games', game.RestGames),
    ('/<token>/info/', 'info', game.RestInfo),
    ('/<token>/draw/', 'draw', game.RestDraw),
    ('/<token>/resign/', 'resign', game.RestResign),
    ('/<token>/moves/', 'moves', game.RestMoves),
])
