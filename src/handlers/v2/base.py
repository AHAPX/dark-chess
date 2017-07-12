from urllib.parse import urljoin

from flask import abort, url_for, request, jsonify, Response, make_response, Blueprint

from cache import get_cache
import config
from errors import BaseException, APIUnauthorized, APIForbidden, APINotFound
from loggers import getLogger
from models import User


logger = getLogger(__name__)


class RestBase():
    auth_required = False
    pre_methods = []

    def __init__(self):
        self.map = {
            'GET': getattr(self, 'get', None),
            'HEAD': getattr(self, 'get', None),
            'POST': getattr(self, 'post', None),
            'DELETE': getattr(self, 'delete', None),
            'PUT': getattr(self, 'put', None),
        }

    def get_methods(self):
        methods = [method for method, func in self.map.items() if func is not None]
        methods.append('OPTIONS')
        return methods

    def get_options_response(self):
        methods = self.get_methods()
        response = jsonify({})
        response.headers['Access-Control-Allow-Methods'] = ', '.join(sorted(x for x in methods))
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', None)
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['X-Clacks-Overhead'] = 'GNU Terry Pratchett'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    def check_authorization(self):
        token = (request.json or {}).get('auth') or \
            request.values.get('auth') or \
            request.cookies.get('auth')
        request.user = None
        request.auth = None
        if token is not None:
            user_id = get_cache(token)
            if user_id:
                try:
                    user = User.get(pk=user_id)
                except User.DoesNotExist:
                    pass
                else:
                    request.user = user
                    request.auth = token

    def __call__(self, *args, **kwargs):
        method = request.method
        if method == 'OPTIONS':
            return self.get_options_response()
        func = self.map.get(method)
        if func is None:
            abort(405)
        result = None
        try:
            assert callable(func)
            self.check_authorization()
            if self.auth_required and not request.user:
                raise APIUnauthorized
            for name in self.pre_methods:
                method = getattr(self, name, None)
                if method and callable(method):
                    result = method(*args, **kwargs)
                    if result:
                        break
            if not result:
                with config.DB.atomic() as transaction:
                    try:
                        result = func(*args, **kwargs)
                    except Exception as e:
                        transaction.rollback()
                        raise e
        except APIUnauthorized as e:
            abort(make_response(e.message, 401))
        except APIForbidden as e:
            abort(make_response(e.message, 403))
        except APINotFound as e:
            abort(make_response(e.message, 404))
        except BaseException as e:
            abort(make_response(e.message, 400))
        except Exception as e:
            logger.error(e)
            abort(500)
        if result is None:
            result = {}
        if isinstance(result, Response):
            return result
        if not isinstance(result, dict):
            result = {'message': result}
        return jsonify(result)


class BlueprintBase(Blueprint):
    def register_blueprint(self, blueprint, **kwargs):
        def deferred(state):
            url_prefix = state.url_prefix or ""
            url_prefix += kwargs.get('url_prefix', blueprint.url_prefix) or ''
            if 'url_prefix' in kwargs:
                del kwargs['url_prefix']
            state.app.register_blueprint(blueprint, url_prefix=url_prefix, **kwargs)
        self.record(deferred)

    def rest(self, url, endpoint, klass):
        assert issubclass(klass, RestBase)
        handler = klass()
        full_url = urljoin(self.url_prefix, url)
        self.add_url_rule(url, endpoint, handler, methods=handler.get_methods())

    def urls(self, urls):
        for url in urls:
            assert len(url) == 3
            self.rest(*url)

    def addChild(self, name, import_name, url_prefix):
        name = '{}.{}'.format(self.name, name)
        url_prefix = '{}{}'.format(self.url_prefix, url_prefix)
        return BlueprintBase(name, import_name, url_prefix=url_prefix)
