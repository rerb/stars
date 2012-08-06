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
        logging.captureWarnings(True)

    def find_in_stack(self, attr):
        for f in inspect.stack():
            if attr in f[0].f_locals:
                return f[0].f_locals[attr]
        return ''

    def process(self, msg, kwargs):
        extra = {'path': '',
                 'host': '',
                 'user': '',
                 'referer': ''}
        try:
            frame = inspect.currentframe()
            caller = frame.f_back.f_back
            module_path = caller.f_globals['__name__']
            extra['module_path'] = module_path
            try:
                request = self.find_in_stack('request')
                if request:
                    extra['request'] = request  # for AdminEmailHandler
                    extra['path'] = request.path
                    try:
                        extra['host'] = request.get_host()
                    except KeyError:  # raised by get_host()
                        pass
                    try:
                        extra['user'] = request.user.username
                    except AttributeError:
                        try:
                            user = self.find_in_stack('user')
                            if user:
                                extra['user'] = user.username
                        finally:
                            if user:
                                del user
                    try:
                        extra['referer'] = request.environ['HTTP_REFERER']
                    except KeyError:  # no referer is ok
                        pass
            finally:
                del request
        finally:
            del module_path, caller, frame
        kwargs['extra'] = extra
        return msg, kwargs
