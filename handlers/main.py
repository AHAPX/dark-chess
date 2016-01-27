from serializers import send_message
from app import app
from decorators import use_cache


@app.route('/')
@use_cache()
def _index():
    return send_message('welcome to dark chess')
