"""
    # Basic doctest suite for Watchdog
    >>> from django.core import management
    >>> from stars.apps.tool.admin.watchdog.models import WatchdogEntry
    >>> from stars.apps.helpers import watchdog
    >>> old_entries = WatchdogEntry.objects.count()

    # Flush the test database in case there are any logged WatchdogEntry's from
    # previous STARS tests
    >>> management.call_command("flush", verbosity=0, interactive=False)

    >>> watchdog.log("Test", "Test notice sent to Watchdog", watchdog.NOTICE)
    >>> watchdog.log("Test", "Test warning sent to Watchdog", watchdog.WARNING)
    >>> watchdog.log("Test", "Test error sent to Watchdog", watchdog.ERROR)

    >>> WatchdogEntry.objects.count() - old_entries
    3
    
    >>> error = WatchdogEntry.objects.all()[0]
    >>> error.message
    u'Test notice sent to Watchdog'
    >>> error.module
    u'Test'
    >>> error.severity
    0
    >>> warning = WatchdogEntry.objects.all()[1]
    >>> warning.message
    u'Test warning sent to Watchdog'
    >>> warning.module
    u'Test'
    >>> warning.severity
    1
    >>> notice = WatchdogEntry.objects.all()[2]
    >>> notice.message
    u'Test error sent to Watchdog'
    >>> notice.module
    u'Test'
    >>> notice.severity
    2
"""
