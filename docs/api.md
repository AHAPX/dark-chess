# API

any response has 'rc' element, for examples:
```
# success
{
    "rc": true,
    "message": "welcome to dark-chess"
}

# failure
{
    "rc": false,
    "error": "wrong move"
}
```
all failure request has 'error' element with description of fail

## applications

### main
- [welcome](main_welcome.md)

### auth
- [registration](auth_register.md)
- [verification](auth_verification.md)
- [login](auth_login.md)
- [logout](auth_logout.md)
 
### game
- [types](game_types.md)
- [new game](game_new.md)
- [game info](game_info.md)
- [do move](game_move.md)
- [draw](game_draw.md)
- [resign](game_resign.md)
- [moves list](game_moves.md)
