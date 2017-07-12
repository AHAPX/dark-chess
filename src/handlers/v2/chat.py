from flask import request

import config
from connections import send_ws
from consts import WS_CHAT_MESSAGE
from decorators import validate
from errors import APIException
from handlers.v2.base import RestBase
from models import ChatMessage
from loggers import logger
from serializers import MessageSerializer
from validators import MessageValidator


class RestMessages(RestBase):
    def get(self):
        try:
            limit = int(request.args.get('limit', -1))
            offset = int(request.args.get('offset', -1))
            if limit < 0:
                limit = config.DEFAULT_COUNT_MESSAGES
            if offset < 0:
                offset = 0
        except Exception as e:
            logger.error(e)
            raise APIException('wrong arguments')
        messages = ChatMessage.select()\
                       .where(ChatMessage.chat == None)\
                       .order_by(-ChatMessage.date_created)\
                       .offset(offset)\
                       .limit(limit)
        return {
            'messages': [MessageSerializer(m).calc() for m in messages],
        }

    @validate(MessageValidator)
    def post(self):
        message = ChatMessage.create(user=request.user, text=self.data['text'])
        result = {'message': MessageSerializer(message).calc()}
        send_ws(result, WS_CHAT_MESSAGE)
        return result
