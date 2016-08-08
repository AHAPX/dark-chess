import config
from app import app


app.run(host=config.HOST, port=config.PORT)
