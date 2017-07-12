from unittest import skip
from unittest.mock import patch

from tests.base import TestCaseWeb
from models import User, ChatMessage
import consts


class TestHandlerChat(TestCaseWeb):
    url_prefix = '/v2/chat/'

    def test_messages_1(self):
        # get messages, should be empty
        resp = self.client.get(self.url('messages/'))
        self.assertEqual(self.load_data(resp), {'messages': []})
        # add message 1
        with patch('handlers.v2.chat.send_ws') as mock:
            resp = self.client.post(self.url('messages/'), data={'text': 'message1'})
            data = self.load_data(resp)
            mock.assert_called_once_with(data, consts.WS_CHAT_MESSAGE)
        self.assertEqual(data['message']['user'], 'anonymous')
        self.assertEqual(data['message']['text'], 'message1')
        dt1 = data['message']['created_at']
        # add message 2
        with patch('handlers.v2.chat.send_ws') as mock:
            resp = self.client.post(self.url('messages/'), data={'text': 'message2'})
            data = self.load_data(resp)
            mock.assert_called_once_with(data, consts.WS_CHAT_MESSAGE)
        self.assertEqual(data['message']['user'], 'anonymous')
        self.assertEqual(data['message']['text'], 'message2')
        dt2 = data['message']['created_at']
        # get messages and check order
        resp = self.client.get(self.url('messages/'))
        expect = {'messages': [
            {'user': 'anonymous', 'text': 'message2', 'created_at': dt2},
            {'user': 'anonymous', 'text': 'message1', 'created_at': dt1},
        ]}
        self.assertEqual(self.load_data(resp), expect)

    def test_message_2(self):
        # login as user and add message
        self.login(*self.add_user('user1', 'password', None))
        resp = self.client.post(self.url('messages/'), data={'text': 'message'})
        data = self.load_data(resp)
        self.assertEqual(data['message']['user'], 'user1')
        self.assertEqual(data['message']['text'], 'message')
        dt = data['message']['created_at']
        # get messages
        resp = self.client.get(self.url('messages/'))
        expect = {'messages': [
            {'user': 'user1', 'text': 'message', 'created_at': dt},
        ]}
        self.assertEqual(self.load_data(resp), expect)

    def test_message_3(self):
        # add messages
        self.client.post(self.url('messages/'), data={'text': 'message1'})
        self.client.post(self.url('messages/'), data={'text': 'message2'})
        self.client.post(self.url('messages/'), data={'text': 'message3'})
        self.client.post(self.url('messages/'), data={'text': 'message4'})
        self.client.post(self.url('messages/'), data={'text': 'message5'})
        # test limit
        resp = self.client.get(self.url('messages/', limit=3))
        data = self.load_data(resp)
        self.assertEqual(len(data['messages']), 3)
        self.assertEqual(data['messages'][0]['text'], 'message5')
        self.assertEqual(data['messages'][1]['text'], 'message4')
        self.assertEqual(data['messages'][2]['text'], 'message3')
        # test offset
        resp = self.client.get(self.url('messages/', offset=2))
        data = self.load_data(resp)
        self.assertEqual(len(data['messages']), 3)
        self.assertEqual(data['messages'][0]['text'], 'message3')
        self.assertEqual(data['messages'][1]['text'], 'message2')
        self.assertEqual(data['messages'][2]['text'], 'message1')
        # test limit and offset
        resp = self.client.get(self.url('messages/', limit=1, offset=3))
        data = self.load_data(resp)
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['text'], 'message2')

