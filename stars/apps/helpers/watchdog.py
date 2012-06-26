from django.http import HttpResponseServerError

import sys

from stars.apps.tool.admin.watchdog.models import WatchdogEntry
from stars.apps.tool.admin.watchdog.models import NOTICE
from stars.apps.tool.admin.watchdog.models import WARNING
from stars.apps.tool.admin.watchdog.models import ERROR
from stars.apps.helpers.exceptions import *

"""
Provides error and notice logging services.
Main api point is watchdog.log - call this to create a log entry.
"""
def log(who, message, severity = NOTICE) :
    """
    Log a system message.   Shamelessly pilfered from Drupal.

    @param who       The module that generated this entry - a short mnemonic < 15 chars.
    @param message   The message to store in the log.
    @param severity  The severity of the message. One of the following values:
                      NOTICE, WARNING, ERROR
    """
    # Because the watchdog is often called when an exception has occurred, 
    # we need to be careful not to generate another exception here, so if we can't do the insert, so be it -
    # that's better than an infinite loop
    if severity != NOTICE:
        print >> sys.stderr, "Watchdog: %s|%s|%s" % (who, message, severity)
    try :
        WatchdogEntry.log(who, message, severity)
    except Exception, e :    
        # there's not much we can do if the DB is down.
        print >> sys.stderr, "Exception: %s"%e

def log_exception(exception):
    """
    Log an exception as an error, and save a copy of the exception object.
    """
    WatchdogEntry.set_exception(exception)

    if ( isinstance(exception, StarsException) ):
        who = exception.who
    else :
        who = exception.__class__.__name__
    log(who, exception.__str__(), ERROR)
    
