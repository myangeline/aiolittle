import asyncio
import functools
import inspect
import logging
import os

from aiohttp import web
from aiohttp.web import Application

from core.utils import join_url


def route(path, methods=None, name=None, expect_handler=None):
    def decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        _wrapper.__route__ = path
        if methods is None:
            m = ['GET']
        elif isinstance(methods, (list, tuple)):
            m = methods
        else:
            m = list(methods)
        _wrapper.__methods__ = m
        # todo 现在 name 和 expect_handler我还不清楚作用，以后添加
        return _wrapper

    return decorator


class SimpleServer(object):
    def __init__(self, router_module=None, app=None, debug=True):
        self.debug = debug
        self._app = app
        self.router_module = router_module if isinstance(router_module, (list, tuple)) else []

    def run(self, host='0.0.0.0', port=None, shutdown_timeout=60.0, ssl_context=None, print=print):
        if self._app is None:
            self._app = Application(debug=self.debug)
        print(self.router_module)
        # map(lambda module_name: self.add_routes(module_name), self.router_module)
        for module_name in self.router_module:
            self.add_routes(module_name)
        web.run_app(self._app, host=host, port=port, shutdown_timeout=shutdown_timeout,
                    ssl_context=ssl_context, print=print)

    def add_route(self, fn, prefix=None):
        methods = getattr(fn, '__methods__', None)
        path = getattr(fn, '__route__', None)
        if path is None or methods is None:
            raise ValueError('@get or @post not defined in %s.' % str(fn))
        if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
            # 将函数变成一个协程,可以异步调用
            fn = asyncio.coroutine(fn)
        path = join_url(prefix, path)
        logging.info('add route %s %s => %s(%s)' % (
            methods, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
        for method in methods:
            self._app.router.add_route(method, path, fn)

    def add_routes(self, module_name, prefix=None):
        n = module_name.rfind('.')
        if n == -1:
            name = None
            mod = __import__(module_name, globals(), locals())
        else:
            name = module_name[n+1:]
            mod = getattr(__import__(module_name[:n], globals(), locals(), (name, )), name)
        for attr in dir(mod):
            if not attr.startswith('-'):
                fn = getattr(mod, attr)
                if callable(fn):
                    methods = getattr(fn, '__methods__', None)
                    path = getattr(fn, '__route__', None)
                    if methods and path:
                        prefix = prefix if prefix else name
                        self.add_route(fn, prefix)

    def add_router_module(self, router_module):
        router_module = router_module if isinstance(router_module, (list, tuple)) else []
        self.router_module = list(set(self.router_module+router_module))

    @property
    def app(self):
        return self._app

