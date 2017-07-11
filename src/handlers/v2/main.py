from handlers.v2.base import RestBase


class RestMain(RestBase):
    def get(self):
        return 'welcome to dark chess'
