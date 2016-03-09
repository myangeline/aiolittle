from aiohttp import web

from core.coreweb import route


@route('/hello')
def hello(request):
    print('request: ', request.host, request.scheme)
    print('hello world')
    return web.Response(body=b"hello aiohttp!")