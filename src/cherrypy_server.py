try:
    from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
except ImportError:
    from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer, WSGIPathInfoDispatcher as PathInfoDispatcher

from src.flask_api import my_app

d = PathInfoDispatcher({'/': my_app})
server = WSGIServer(('0.0.0.0', 80), d)

if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()