from jinja2 import Environment, FileSystemLoader
from webob.request import Request as WebObRequest
from webob.response import Response as WebObResponse
from webob.dec import wsgify
from webob import exc
from wsgiref.simple_server import make_server
import sys
import os
import re

__all__ = [
    'PyBoa',
    'make_response',
    'render_template'
]

_jinja_env = Environment(loader=FileSystemLoader(os.path.abspath('./templates')))

# 匹配路由的正则表达式
rule_regex = re.compile(r'''
      \{
      (\w+)
      (?::([^}]+))?
      \}
      ''', re.VERBOSE)

def _is_immutable(self):
    raise TypeError('%r objects are immutable' % self.__class__.__name__)

iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))

class ImmutableDictMixin(object):
    _hash_cache = None

    def __setitem__(self, key, value):
        _is_immutable(self)

    def __delitem__(self, key):
        _is_immutable(self)

    def clear(self):
        _is_immutable(self)

    def pop(self):
        _is_immutable(self)

    def update(self):
        _is_immutable(self)

    def setdefault(self):
        _is_immutable(self)

    def _iter_hashitems(self):
        return iteritems(self)

    def __hash__(self):
        if self._hash_cache is not None:
            return self._hash_cache
        rv = self._hash_cache = hash(frozenset(self._iter_hashitems()))
        return rv


class ImmutableDict(ImmutableDictMixin, dict):
    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            dict.__repr__(self),
        )

    def copy(self):
        return dict(self)

    def __copy__(self):
        return self
        

class Request(WebObRequest):
    pass


class Response(WebObResponse):
    content_type = 'text/html'

wsgify.RequestClass = Request


def make_response(**options):
    resp = Response(**options)
    return resp

def render_template(template_name, **context):
    return _jinja_env.get_template(template_name).render(context)

def load_controller(string):
    module_name, func_name = string.split(':', 1)
    if module_name:
        __import__(module_name)
    else:
        file_path = sys._getframe(2).f_code.co_filename.replace('.py', '')
        module_name = os.path.basename(file_path)
        __import__(module_name)
    module = sys.modules[module_name]
    func = getattr(module, func_name)
    func = wsgify(func)
    return func


class Config(dict):
    def from_object(self, obj):
        for key in dir(obj):
            # 检查所有字母是否均为大写,是则视为配置参数
            if key.isupper():
                self[key] = obj


class PyBoa(object):
    default_config = ImmutableDict({
        'DEBUG':        True,
    })

    def __init__(self):
        self.routes = []
        self.config = Config(self.default_config)

    def add_route(self, template, controller, **options):
        if isinstance(controller, str):
            controller = load_controller(controller)
        options.setdefault('methods', ('GET', ))
        self.routes.append((re.compile(rule_to_regex(template)),
                            controller,
                            options))

    def __call__(self, environ, start_response):
        req = Request(environ)
        for regex, controller, options in self.routes:
          match = regex.match(req.path_info)
          if match:
              if req.method not in options['methods']:
                  # methods参数
                  return exc.HTTPMethodNotAllowed()(environ, start_response)
              req.urlvars = match.groupdict()
              req.urlvars.update(options)
              return controller(environ, start_response)
        return exc.HTTPNotFound()(environ, start_response)

    def route(self, rule, **options):
        def decorator(view):
            view = wsgify(view)
            self.add_route(rule, controller=view, **options)
            return view
        return decorator

    def run(self, host='127.0.0.1', port=8000, **options):
        server = make_server(host, port, self)
        print("Serving on port {}...".format(port))
        try:
            server.serve_forever()
        except:
            server.shutdown()


def rule_to_regex(rule):
    regex = ''
    last_pos = 0
    for match in rule_regex.finditer(rule):
        regex += re.escape(rule[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(rule[last_pos:])
    regex = '^%s$' % regex
    return regex

