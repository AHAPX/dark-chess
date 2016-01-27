from serializers import send_message
from app import app


@app.route('/')
def _index():
    return send_message('welcome to dark chess')
