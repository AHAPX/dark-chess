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
        try:
            limit = int(request.args.get('limit', -1))
            offset = int(request.args.get('offset', -1))
            if limit < 0:
                limit = config.DEFAULT_COUNT_MESSAGES
            if offset < 0:
                offset = 0
        except Exception as e:
            log.error(e)
            return send_error('wrong arguments')
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
