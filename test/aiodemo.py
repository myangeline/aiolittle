from core.coreweb import SimpleServer

server = SimpleServer(['handler1'])
server.add_router_module(['handler1', 'handlers.handler2'])
server.run()
