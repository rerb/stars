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
        WatchdogContact.notify(entry)
    log = classmethod(log)
    
    def __str__(self):
        user = "USER : %s " % self.user
        path = "PATH: %s " % self.request_path
        view = ""
            
        return "Watchdog %s (%s): %s (%s, %s)" % (SEVERITY_CLASSES[self.severity][1], self.module, self.message, user, path)

#    @staticmethod
    def get_admin_url():
        return "/tool/admin/watchdog/"
    get_admin_url = staticmethod(get_admin_url)

    def get_absolute_url(self):
        return "%s%s/" % (self.get_admin_url(), self.id)
    
    def get_severity(self):
        return SEVERITY_CLASSES[self.severity][1]
    
    MESSAGE_TEMPLATE = """ {% autoescape off %}
        STARS Watchdog logged the following {{entry.get_severity_display}}:
        {{entry.get_severity}}: {{ entry.message }}
        Module: {{entry.module}}
        Path: {{entry.request_path}}
        Referer: {{entry.request_referer}}
        Host: {{entry.request_host}}
        User: {{entry.user}}
        Timestamp: {{entry.timestamp.ctime}}
        {% endautoescape %}
    """
    
    def get_formatted_message(self):
        """
            Format an e-mail message with the information from this entry
        """
        from django.template import Context, Template
        t = Template(self.MESSAGE_TEMPLATE)
        c = Context({"entry": self})
        return t.render(c)
    
    def save(self):
        """
        We need to be a bit careful here since the Watchdog gets called when things go wrong!
        The DB might be out - if we can't save the record, try printing it.
        """
        import sys
        try:
            super(WatchdogEntry, self).save()
            if settings.DEBUG and not settings.TESTING:
                print >> sys.stderr, self
        except Exception, e: # oh well - not much we can do if we can't even log an error!
            if settings.DEBUG and not settings.TESTING:
                # @todo: consider using warning.warn here...
                print >> sys.stderr, "Unable to save WatchdogEntry : %s"%e
                print >> sys.stderr, self
   
class WatchdogContact(models.Model):
    """
        An person who should receive notification about watchdog entries
    """
    user = models.ForeignKey(User)                                  # user to notify
    alternate_email = models.EmailField("Alternate Email", blank=True, null=True, help_text="Only specify an alternate e-mail if you want notifications to go to a different e-mail than your default one.")
    severity = models.SmallIntegerField(choices=SEVERITY_CLASSES, help_text="Minimum severity class to recieve notificaiton on - notification will be sent for all entrtries with at least this severity.")   

    class Meta:
        unique_together = ("user", "alternate_email")

    @staticmethod
    def notify(watchdog_entry):
        """ Notify all Watchdog contacts who are interested in the given entry """
        if not settings.DEBUG:
            from django.core.mail import send_mail
            contacts = WatchdogContact.objects.filter(severity__lte = watchdog_entry.severity)
            contact_emails = []
            for contact in contacts:
                email = contact.alternate_email if contact.alternate_email else contact.user.email
                contact_emails.append(email)
            
            if contact_emails:
                send_mail('STARS Watchdog: %s notification'%watchdog_entry.get_severity_display(), \
                          watchdog_entry.get_formatted_message(), settings.EMAIL_HOST_USER, \
                          contact_emails, fail_silently=True )
