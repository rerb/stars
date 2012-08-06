"""Logging bits for STARS.

Usage:

    from stars.apps.helpers import logging
    logger = logging.getLogger(__name__)
"""
import inspect
import logging

def getLogger(name=None):
    logger = logging.getLogger(name)
    return StarsLoggerAdapter(logger)


class StarsLoggerAdapter(logging.LoggerAdapter):
    """This LoggerAdapter adds the following fields to a LogMessage:

           - path
           - host
           - user
           - referer
           - module_path

    Path, host, user, and referer are pulled from a request in the
    caller's locals(), if there's a request there.
    """

    def __init__(self, logger, extra=None):
        logging.LoggerAdapter.__init__(self, logger, extra or {})

    def process(self, msg, kwargs):
        extra = {'path': '-',
                 'host': '-',
                 'user': '-',
                 'referer': '-'}
        try:
            frame = inspect.currentframe()
            caller = frame.f_back.f_back
            caller_locals = caller.f_locals
            try:
                caller_module = caller_locals['self'].__module__
            except KeyError:
                # no self? let's try one step back:
                try:
                    caller_module = caller.f_back.f_locals['self'].__module__
                except KeyError:
                    # still no self? let's use __name__:
                    caller_module = caller.f_globals['__name__']
            extra['module_path'] = caller_module
            try:
                request = caller_locals['request']
                extra['path'] = request.path
                extra['host'] = request.get_host()
                extra['user'] = request.user.username or 'anonymous'
                try:
                    extra['referer'] = request.environ['HTTP_REFERER']
                except KeyError:  # no referer is ok
                    pass
            except KeyError:  # no request in the caller
                pass
            else:
                del request
        finally:
            del caller_module, caller_locals, caller, frame
        kwargs['extra'] = extra
        return msg, kwargs
