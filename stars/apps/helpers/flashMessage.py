
"""
Severity classes for Flash Messenger:
Notice messages are normally notifications of normal events that have occurred - no action required by user.
Success messages notify the user that an action they initiated completed successfully.
Error  messages are sent when a user has made an error or taken an action that could not be completed.
"""
NOTICE = 0
SUCCESS = 1
ERROR = 2

MESSAGE_CLASSES = ["notice", "success", "error"]  # correspond to CSS classes used to display messages.


"""
Provides messaging services to pass messages to the UI easily from anywhere.
Wrapper for the Django light-weight messaging service: http://docs.djangoproject.com/en/dev/topics/auth/#messages
Main api point is flashMessage.add_message - call this to send a message to the user.
"""
def send(message, msg_class=NOTICE) :
    """
    Store a message to be sent to the user on the next response.
    Messages can only be sent to authenticated users - not anonymous users.
    @param message  message text to flash to user.  May be None - no message will be sent.
    @param msg_class  message class -one of: NOTICE, SUCCESS, or ERROR
    """    
    user = FlashMessageMiddleware.user
    if (message and user is not None and user.is_authenticated()):
        # hack - cache the class within the message itself.  @todo: replace Django messaging with custom message management that includes a message class
        #      - works closely with 'split' helper tag, which uses the separator used here to split out the message class for display.
        message = "%s::%s"%(MESSAGE_CLASSES[msg_class], message)
        FlashMessageMiddleware.user.message_set.create(message=message)
    # In future, if we wanted to send messages to anon. users, we could
    # store messages in a list in the session here, then retrieve them
    # using a context processor or middleware.

class FlashMessageMiddleware :
    """
    Provides middleware services for passing messages to the user
    The flash message service only works if the FlashMessage middleware is added to setting.MIDDLEWARE_CLASSES
    """
    user = None

    def process_request(self, request) :
        """
        Called just before the View is processed.
        Stores information about the request in case its needed by watchdog
        """
        FlashMessageMiddleware.user = request.user
        # Always return None so that view continues to be processed normally!
        return None
    
