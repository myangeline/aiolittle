from aiohttp import web

from core.coreweb import route


@route('/hello2/{name}')
def hello2(request):
    print(request)
    # print(name)
    print(request.app)
    print(request.match_info)
    return web.Response(body="hello 2 request!".encode())
