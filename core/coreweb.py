import asyncio
import functools
import inspect
import logging

from aiohttp.web import RequestHandler


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


def add_route(app, fn):
    methods = getattr(fn, '__methods__')
    path = getattr(fn, '__route__')
    if path is None or methods is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (
        methods, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    for method in methods:
        app.router.add_route(method, path, RequestHandler(app, fn))
