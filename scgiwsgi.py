# https://github.com/dengzhp/scgiwsgi
import os
import socket
import sys

from scgi import scgi_server
from scgi import passfd

__all__ = ['WSGIServer']

__version__ = "0.1"


_application = None
_logger = None

def build_wsgi_environ(scgi_env, scgi_input):
    environ = {}
    environ['wsgi.input']        = scgi_input
    environ['wsgi.errors']       = sys.stderr
    environ['wsgi.version']      = (1, 0)
    environ['wsgi.multithread']  = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once']     = False
    environ['wsgi.url_scheme']   = 'http'
    for k in scgi_env:
        if k != "SCGI":
            if k == 'DOCUMENT_URI':
                environ['PATH_INFO'] = scgi_env[k]
            else:
                environ[k] = scgi_env[k]

    environ['SCRIPT_NAME'] = ''
    return environ

class WsgiHandler(scgi_server.SCGIHandler):

    def serve(self):
        while 1:
            try:
                os.write(self.parent_fd, "1") # indicates that child is ready
                fd = passfd.recvfd(self.parent_fd)
            except (IOError, OSError):
                if _logger:
                    _logger.exception('exiting')
                # parent probably exited  (EPIPE comes thru as OSError)
                raise SystemExit
            conn = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
            # Make sure the socket is blocking.  Apparently, on FreeBSD the
            # socket is non-blocking.  I think that's an OS bug but I don't
            # have the resources to track it down.
            conn.setblocking(1)
            os.close(fd)
            try:
                self.handle_connection(conn)
            except Exception:
                if _logger:
                    _logger.exception('exception occured')
                else:
                    raise

    def handle_connection(self, conn):
        input = conn.makefile("r")
        output = conn.makefile("w")
        env = self.read_env(input)
        environ = build_wsgi_environ(env, input)

        headers_set = []
        headers_sent = []

        def wsgi_write(data):
            if not isinstance(data, str):
                raise TypeError("application must return an iterable yielding zero or more strings")

            if not headers_set:
                raise AssertionError("write() before start_response()")

            elif not headers_sent:
                # Before the first output, send the stored headers
                status, headers = headers_sent[:] = headers_set

                output.write("HTTP/1.1 %s\r\n" % status)
                for h in headers:
                    output.write("%s: %s\r\n" % (h[0], h[1]))
                output.write("\r\n")

            output.write(data)

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None     # avoid dangling circular ref
            elif headers_set:
                raise AssertionError("Headers already set!")

            headers_set[:] = [status, response_headers]

            return wsgi_write

        try:
            result = _application(environ, start_response)

            try:
                for data in result:
                    if data:    # don't send headers until body appears
                        wsgi_write(data)

                if not headers_sent:
                    wsgi_write('')   # send headers now if body was empty
            finally:
                if hasattr(result, 'close'):
                    result.close()

        finally:
            output.close()
            input.close()
            conn.close()


class WSGIServer:
    def __init__(self, app, logger=None):
        global _application, _logger
        _application = app
        _logger = logger

    def run(self, host='', port=4000, max_children=5):
        scgi_server.SCGIServer(handler_class=WsgiHandler,
                               host=host,
                               port=port,
                               max_children=max_children).serve()


if __name__ == "__main__":
    from app import application
    import logging
    logger = logging.getLogger()
    WSGIServer(application, logger).run(port=4000)

