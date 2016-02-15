#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from tornado.options import options, define, parse_command_line
# import django.core.handlers.wsgi
from django.core.wsgi import get_wsgi_application
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = "saplatform.settings"

define('port', type=int, default=8088)


def main():
    parse_command_line()

    # wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())

    tornado_app = tornado.web.Application([('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)), ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
