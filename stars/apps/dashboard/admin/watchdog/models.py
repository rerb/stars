from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

"""
    Back-end for Watchdog error logging system
    Clients should NOT use this class directly 
      --> use helpers.watchdog.log() function to log messages!!
"""

"""
    Watchdog log entries expire after this period (specified as datetime.timedelta dictionary)
    Once expired, they may be purged from the DB by visiting the appropriate view
"""
LOG_DURATION = {"days":7}   # log entries endure for a week.

"""
Severity Level for Watchdog log entries:
Notice level events are normally notifications of normal system events that have occurred and can usually be safely ignored.
Warning level events can be triggered by an error that does not impact the overall functionality of the site.
Error level events could be indicative of an attempt to compromise the security of the site, or a serious system error.
"""
NOTICE = 0
WARNING = 1
ERROR = 2

SEVERITY_CLASSES = (
    (NOTICE, "Notice"),
    (WARNING, "Warning"),
    (ERROR, "Error"),
)
 
class WatchdogEntry(models.Model):
    """
        An entry in the watchdog log
        A watchdog entry attempts to record as much info about the request
            as possible, along with the log message.
    """
    user = models.ForeignKey(User, blank=True, null=True)           # user on the request
    module = models.CharField(max_length=15, blank=True, null=True) # module that generated log entry
    message = models.TextField()                                    # log message
    severity = models.SmallIntegerField(choices=SEVERITY_CLASSES)            
    request_path = models.URLField(blank=True, null=True)           # request location
    request_referer = models.URLField(blank=True, null=True)        # referer, if available
    request_host = models.TextField(blank=True, null=True)          # host that made request, if available
    timestamp = models.DateTimeField(auto_now_add=True)

    request = None
    view = None
    exception = None

    class Meta:
        ordering = ('-timestamp',)     
        verbose_name_plural = "Watchdog Entries"
        
#    @classmethod
    def set_request(cls, request, view_func):
        """  
            Store information about the request to log with any watchdog message
            This is called by the watchdog middleware for each request.
        """
        cls.request = request
        cls.view = view_func
    set_request = classmethod(set_request)
    
#    @classmethod
    def set_exception(cls, exception):
        """  
            Store information about an exception to log with any watchdog message
            This is called by the watchdog middleware during exception handling.
        """
        cls.exception = exception
    set_exception = classmethod(set_exception)
    
#    @classmethod
    def log(cls, who, message, severity):
        """
        Log a new entry for the watchdog log.
        @param who       The module that generated this message.
        @param message   The message to store in the log.
        @param severity  The severity of the message. One of the following values:
                          NOTICE, WARNING, ERROR
        """
        user = None
        path = None
        host = None
        referer = None
        if cls.request:
            if cls.request.user.is_authenticated():
                user = cls.request.user
            path = cls.request.build_absolute_uri()
            host = cls.request.get_host()
            if cls.request.META.has_key('HTTP_REFERER'):
                referer = cls.request.META['HTTP_REFERER']
        entry = WatchdogEntry(module=who, message=message, 
                              severity=severity, user=user, 
                              request_path=path, request_host=host,
                              request_referer=referer)
        entry.save()
    log = classmethod(log)
    
    def __str__(self):
        user = "USER : %s " % self.user
        path = "PATH: %s " % self.request_path
        view = ""
            
        return "Watchdog %s (%s): %s (%s, %s)" % (SEVERITY_CLASSES[self.severity][1], self.module, self.message, user, path)

#    @staticmethod
    def get_admin_url():
        return "/dashboard/admin/watchdog/"
    get_admin_url = staticmethod(get_admin_url)

    def get_absolute_url(self):
        return "%s%s/" % (self.get_admin_url(), self.id)
    
    def get_severity(self):
        return SEVERITY_CLASSES[self.severity][1]
    
    def save(self):
        """
        We need to be a bit careful here since the Watchdog gets called when things go wrong!
        The DB might be out - if we can't save the record, try printing it.
        """
        try:
            super(WatchdogEntry, self).save()
            if settings.DEBUG and not settings.TESTING:
                print self
        except Exception, e: # oh well - not much we can do if we can't even log an error!
            if settings.DEBUG and not settings.TESTING:
                # @todo: consider using warning.warn here...
                print "Unable to save WatchdogEntry : %s"%e
                print self
    