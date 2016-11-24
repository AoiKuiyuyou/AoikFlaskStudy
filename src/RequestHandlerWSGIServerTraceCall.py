# coding: utf-8
from __future__ import absolute_import

# Standard imports
import sys
import logging

# External imports
import aoiktracecall.config
import aoiktracecall.logging
import aoiktracecall.trace


# Traced modules should be imported after `trace_calls_in_specs` is called.


# Set configs
aoiktracecall.config.set_configs({
    # Whether use wrapper class.
    #
    # Wrapper class is more adaptive to various types of callables but will
    # break if the code that was using the original function requires a real
    # function, instead of a callable. Known cases include PyQt slot functions.
    #
    'WRAP_USING_WRAPPER_CLASS': True,

    # Whether wrap base class attributes in a subclass.
    #
    # If enabled, wrapper attributes will be added to a subclass even if the
    # wrapped original attributes are defined in a base class.
    #
    # This helps in the case that base class attributes are implemented in C
    # extensions thus can not be traced directly.
    #
    'WRAP_BASE_CLASS_ATTRIBUTES': True,

    # Whether highlight title shows `self` argument's class instead of called
    # function's defining class.
    #
    # This helps reveal the real type of the `self` argument on which the
    # function is called.
    #
    'HIGHLIGHT_TITLE_SHOW_SELF_CLASS': True,

    # Highlight title line character count max
    'HIGHLIGHT_TITLE_LINE_CHAR_COUNT_MAX': 265,

    # Whether show function's file path and line number in pre-call hook
    'SHOW_FUNC_FILE_PATH_LINENO_PRE_CALL': True,

    # Whether show function's file path and line number in post-call hook
    'SHOW_FUNC_FILE_PATH_LINENO_POST_CALL': False,

    # Whether wrapper function should debug info dict's URIs
    'WRAPPER_FUNC_DEBUG_INFO_DICT_URIS': False,

    # Whether printing handler should debug arguments inspect info
    'PRINTING_HANDLER_DEBUG_ARGS_INSPECT_INFO': False,

    # Whether printing handler should debug info dict.
    #
    # Notice info dict contains called function's arguments and printing these
    # arguments may cause errors.
    #
    'PRINTING_HANDLER_DEBUG_INFO_DICT': False,

    # Whether printing handler should debug info dict, excluding arguments.
    #
    # Use this if `PRINTING_HANDLER_DEBUG_INFO_DICT` causes errors.
    #
    'PRINTING_HANDLER_DEBUG_INFO_DICT_SAFE': False,
})


# Add debug logger handler
aoiktracecall.logging.get_debug_logger().addHandler(logging.NullHandler())

# Add info logger handler
aoiktracecall.logging.get_info_logger().addHandler(
    logging.StreamHandler(sys.stdout)
)

# Add error logger handler
aoiktracecall.logging.get_error_logger().addHandler(
    logging.StreamHandler(sys.stderr)
)


# Constant for `highlight`
HL = 'highlight'

# Create trace specs.
#
# The order of the specs determines the matching precedence, with one exception
# that URI patterns consisting of only alphanumerics, underscores, and dots are
# considered as exact URI matching, and will have higher precedence over all
# regular expression matchings. The rationale is that a spec with exact URI
# matching is more specific therefore should not be shadowed by any spec with
# regular expression matching that has appeared early.
#
trace_specs = [
    # ----- aoiktracecall -----
    ('aoiktracecall([.].+)?', False),

    # ----- * -----
    # Tracing `__setattr__` will reveal instances' attribute assignments.
    # Notice Python 2 old-style classes have no `__setattr__` attribute.
    ('.+[.]__setattr__', True),

    # Not trace most of double-underscore functions.
    # Tracing double-underscore functions is likely to break code, e.g. tracing
    # `__str__` or `__repr__` may cause infinite recursion.
    ('.+[.]__(?!init|call)[^.]+__', False),

    # ----- socket._socketobject (Python 2), socket.socket (Python 3) -----
    # Notice in Python 2, class `socket._socketobject`'s instance methods
    # - recv
    # - recvfrom
    # - recv_into
    # - recvfrom_into
    # - send
    # - sendto
    # are dynamically generated in `_socketobject.__init__`. The approach of
    # wrapping class attributes is unable to trace these methods.

    ('socket[.](_socketobject|socket)[.]__init__', HL),

    ('socket[.](_socketobject|socket)[.]bind', HL),

    ('socket[.](_socketobject|socket)[.]listen', HL),

    ('socket[.](_socketobject|socket)[.]connect', HL),

    ('socket[.](_socketobject|socket)[.]accept', HL),

    ('socket[.](_socketobject|socket)[.]setblocking', HL),

    ('socket[.](_socketobject|socket)[.]makefile', HL),

    ('socket[.](_socketobject|socket)[.]recv.*', HL),

    ('socket[.](_socketobject|socket)[.]send.*', HL),

    ('socket[.](_socketobject|socket)[.]shutdown', HL),

    ('socket[.](_socketobject|socket)[.]close', HL),

    # ----- socket._fileobject (Python 2), socket.SocketIO (Python 3) -----
    ('socket[.](SocketIO|_fileobject)[.]__init__', HL),

    ('socket[.](SocketIO|_fileobject)[.]read.*', HL),

    ('socket[.](SocketIO|_fileobject)[.]write.*', HL),

    ('socket[.](SocketIO|_fileobject)[.]flush', HL),

    ('socket[.](SocketIO|_fileobject)[.]close', HL),

    ('socket[.](SocketIO|_fileobject)[.].+', True),

    # ----- socket -----
    ('socket._intenum_converter', False),

    ('socket[.].+[.]_decref_socketios', False),

    ('socket[.].+[.]fileno', False),

    # Ignore to avoid error in `__repr__` in Python 3
    ('socket[.].+[.]getpeername', False),

    # Ignore to avoid error in `__repr__` in Python 3
    ('socket[.].+[.]getsockname', False),

    ('socket[.].+[.]gettimeout', False),

    ('socket([.].+)?', True),

    # ----- select (Python 2) -----
    ('select.select', HL),

    ('select([.].+)?', True),

    # ----- selectors (Python 3) -----
    ('selectors.SelectSelector.__init__', HL),

    ('selectors.SelectSelector.register', HL),

    ('selectors.SelectSelector.select', HL),

    ('selectors([.].+)?', True),

    # ----- SocketServer (Python 2), socketserver (Python 3) -----
    ('SocketServer._eintr_retry', False),

    ('(socketserver|SocketServer)[.]BaseServer[.]__init__', HL),

    ('(socketserver|SocketServer)[.]TCPServer[.]__init__', HL),

    ('(socketserver|SocketServer)[.]ThreadingMixIn[.]process_request', HL),

    (
        '(socketserver|SocketServer)[.]ThreadingMixIn[.]'
        'process_request_thread', HL
    ),

    # Ignore to avoid error:
    # ```
    # 'WSGIServer' object has no attribute '_BaseServer__is_shut_down'
    # ```
    ('(socketserver|SocketServer)[.]ThreadingMixIn[.].+', False),

    ('(socketserver|SocketServer)[.]BaseRequestHandler[.]__init__', HL),

    ('(socketserver|SocketServer)[.].+[.]service_actions', False),

    ('.+[.]server_bind', HL),

    ('.+[.]server_activate', HL),

    ('.+[.]serve_forever', HL),

    ('.+[.]_handle_request_noblock', HL),

    ('.+[.]get_request', HL),

    ('.+[.]verify_request', HL),

    ('.+[.]process_request', HL),

    ('.+[.]process_request_thread', HL),

    ('.+[.]finish_request', HL),

    ('.+[.]setup', HL),

    ('.+[.]handle', HL),

    ('.+[.]finish', HL),

    ('.+[.]shutdown_request', HL),

    ('.+[.]close_request', HL),

    ('.+[.]fileno', False),

    ('(socketserver|SocketServer)([.].+)?', True),

    # ----- mimetools -----
    # `mimetools` is used for parsing HTTP headers in Python 2.

    ('mimetools([.].+)?', True),

    # ----- email -----
    # `email` is used for parsing HTTP headers in Python 3.

    ('email([.].+)?', True),

    # ----- BaseHTTPServer (Python 2), http.server (Python 3) -----
    ('.+[.]handle_one_request', HL),

    ('.+[.]parse_request', HL, 'hide_below'),

    ('.+[.]send_response', HL),

    ('.+[.]send_header', HL),

    ('.+[.]end_headers', HL),

    # ----- BaseHTTPServer (Python 2) -----
    ('BaseHTTPServer([.].+)?', True),

    # ----- http (Python 3) -----
    ('http([.].+)?', True),

    # ----- wsgiref -----
    ('wsgiref.handlers.BaseHandler.write', HL),

    ('wsgiref.handlers.BaseHandler.close', HL),

    ('wsgiref.handlers.SimpleHandler.__init__', HL),

    ('wsgiref.handlers.SimpleHandler._write', HL),

    ('wsgiref.handlers.SimpleHandler._flush', HL),

    ('wsgiref.simple_server.WSGIServer.__init__', HL),

    ('wsgiref.simple_server.ServerHandler.__init__', HL),

    ('wsgiref.simple_server.ServerHandler.close', HL),

    ('.+[.]make_server', HL),

    ('.+[.]setup_environ', HL, 'hide_below'),

    ('.+[.]set_app', HL),

    ('.+[.]get_environ', HL, 'hide_below'),

    ('.+[.]get_app', HL),

    ('.+[.]run', HL),

    ('.+[.]start_response', HL),

    ('.+[.]finish_response', HL),

    ('.+[.]send_headers', HL),

    ('.+[.]cleanup_headers', HL),

    ('.+[.]send_preamble', HL),

    ('.+[.]finish_content', HL),

    ('.+[.]finish', HL),

    ('wsgiref([.].+)?', True),

    # ----- flask -----
    ('flask.app.Flask.__call__', HL),

    ('flask.app.Flask.__init__', HL),

    # Ignore to avoid error
    ('flask.app.Flask.__setattr__', False),

    ('flask.app.Flask.add_url_rule', HL),

    ('flask.app.Flask.app_context', HL),

    ('flask.app.Flask.create_url_adapter', HL),

    ('flask.app.Flask.dispatch_request', HL),

    ('flask.app.Flask.do_teardown_appcontext', HL),

    ('flask.app.Flask.do_teardown_request', HL),

    ('flask.app.Flask.full_dispatch_request', HL),

    ('flask.app.Flask.make_null_session', HL),

    ('flask.app.Flask.make_response', HL),

    ('flask.app.Flask.open_session', HL),

    ('flask.app.Flask.preprocess_request', HL),

    ('flask.app.Flask.process_response', HL),

    ('flask.app.Flask.request_class', HL),

    ('flask.app.Flask.request_context', HL),

    ('flask.app.Flask.response_class', HL),

    ('flask.app.Flask.route', HL),

    ('flask.app.Flask.try_trigger_before_first_request_functions', HL),

    ('flask.app.Flask.wsgi_app', HL),

    ('flask.ctx.AppContext.__init__', HL),

    ('flask.ctx.AppContext.pop', HL),

    ('flask.ctx.AppContext.push', HL),

    ('flask.ctx.RequestContext.__init__', HL),

    # Ignore to avoid error
    ('flask.ctx.RequestContext.__setattr__', False),

    ('flask.ctx.RequestContext.auto_pop', HL),

    ('flask.ctx.RequestContext.match_request', HL),

    ('flask.ctx.RequestContext.pop', HL),

    ('flask.ctx.RequestContext.push', HL),

    ('flask.helpers._PackageBoundObject.__init__', HL),

    # Ignore to avoid error
    ('flask.helpers._PackageBoundObject.__setattr__', False),

    ('flask.signals._FakeSignal.send', HL),

    ('flask([.].+)?', True),

    # ----- __main__ -----
    ('__main__.main', HL),

    ('__main__.CustomRequestHandler', HL),

    ('__main__([.].+)?', True),
]


# Create `printing_handler`'s filter function
def printing_handler_filter_func(info):
    # Get on-wrap URI
    onwrap_uri = info['onwrap_uri']

    # If is one of these URIs
    if onwrap_uri in {
        'flask.app.Flask.__call__',
        'flask.app.Flask.request_class',
        'flask.app.Flask.request_context',
        'flask.app.Flask.wsgi_app',
        'flask.ctx.RequestContext.__init__',
        'flask.wrappers.Request.__init__',
        'flask.wrappers.Response.__call__',
        'flask.wrappers.Response.get_app_iter',
        'flask.wrappers.Response.get_wsgi_headers',
        'flask.wrappers.Response.get_wsgi_response',
    }:
        # Get arguments inspect info
        arguments_inspect_info = info['arguments_inspect_info']

        # Get `environ` argument info
        arg_info = arguments_inspect_info.fixed_arg_infos['environ']

        # Hide value
        arg_info.value = '{...}'

    # If is this URI:
    if onwrap_uri == 'flask.wrappers.Request.__setattr__':
        # Get arguments inspect info
        arguments_inspect_info = info['arguments_inspect_info']

        # Get `name` argument info
        name_arg_info = arguments_inspect_info.fixed_arg_infos['name']

        # If `name` argument's value is `environ`
        if name_arg_info.value == 'environ':
            # Get `value` argument info
            value_arg_info = arguments_inspect_info.fixed_arg_infos['value']

            # Hide value
            value_arg_info.value = '{...}'

    # Return info dict
    return info


# Trace calls according to trace specs.
#
# This function will hook the module importing system in order to intercept and
# process newly imported modules. Callables in these modules which are matched
# by one of the trace specs will be wrapped to enable tracing.
#
# Already imported modules will be processed as well. But their callables may
# have been referenced elsewhere already, making the tracing incomplete. This
# explains why import hook is needed and why modules must be imported after
# `trace_calls_in_specs` is called.
#
aoiktracecall.trace.trace_calls_in_specs(
    specs=trace_specs,
    printing_handler_filter_func=printing_handler_filter_func,
)

# Remove to avoid being traced
del printing_handler_filter_func


# Import modules after `trace_calls_in_specs` is called
from wsgiref.simple_server import make_server
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import WSGIServer

import flask


# Notice do not use decorator to add URL-to-handler mapping here otherwise this
# function can not be traced.
#
def CustomRequestHandler():
    """
    This request handler echoes request body in response body.
    """
    # Read request body
    request_body = flask.request.get_data()

    # Return response body
    return request_body


def main():
    # Create application
    flask_app = flask.Flask(__name__)

    # Add URL-to-handler mapping
    flask_app.route('/', methods=['POST'])(CustomRequestHandler)

    try:
        # Create server
        server = make_server(
            host='127.0.0.1',
            port=8000,
            app=flask_app,
            server_class=WSGIServer,
            handler_class=WSGIRequestHandler,
        )

        # Run server
        server.serve_forever()

    # If have `KeyboardInterrupt`
    except KeyboardInterrupt:
        # Stop gracefully
        pass


# Trace calls in this module.
#
# Calling this function is needed because at the point `trace_calls_in_specs`
# is called, this module is being initialized, therefore callables defined
# after the call point are not accessible to `trace_calls_in_specs`.
#
aoiktracecall.trace.trace_calls_in_this_module()


# If is run as main module
if __name__ == '__main__':
    # Call main function
    exit(main())
