from handlers.v2 import main, auth
from handlers.v2.base import BlueprintBase


bp = BlueprintBase('v2', __name__, url_prefix='/v2')
bp.urls([
    ('/', 'home', main.RestMain),
])


bp_auth = bp.addChild('auth', __name__, url_prefix='/auth')
bp_auth.urls([
    ('/register/', 'register', auth.RestRegister),
    ('/verification/', 'verification', auth.RestVerification),
    ('/verification/<token>/', 'verification_confirm', auth.RestVerificationConfirm),
    ('/reset/', 'reset', auth.RestReset),
    ('/recover/<token>/', 'recover', auth.RestRecover),
    ('/login/', 'login', auth.RestLogin),
    ('/logout/', 'logout', auth.RestLogout),
])
