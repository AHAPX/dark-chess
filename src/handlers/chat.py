from flask import request, Blueprint

import errors
import config
import consts
from serializers import send_data, send_error, MessageSerializer
from validators import MessageValidator
from decorators import authenticated, validated
from models import Chat, ChatMessage
from connections import send_ws


bp = Blueprint('chat', __name__, url_prefix='/v1/chat')


@bp.route('/messages', methods=['GET', 'POST'])
@authenticated
def messages():

    @validated(MessageValidator)
    def _post(data):
        message = ChatMessage.create(user=request.user, text=data['text'])
        result = {'message': MessageSerializer(message).calc()}
        send_ws(result, consts.WS_CHAT_MESSAGE)
        return send_data(result)

    if request.method == 'GET':
        limit = request.args.get('limit', config.DEFAULT_COUNT_MESSAGES)
        offset = request.args.get('offset', 0)
        if limit < 0:
            limit = 0
        if offset < 0:
            offset = 0
        messages = ChatMessage.select()\
                       .where(ChatMessage.chat == None)\
                       .order_by(-ChatMessage.date_created)\
                       .offset(offset)\
                       .limit(limit)
        return send_data({
            'messages': [MessageSerializer(m).calc() for m in messages],
        })
    elif request.method == 'POST':
        return _post()
