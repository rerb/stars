"""
    PermMixin Doctests
    
    Test Premises:
     - authenticates with permissions
         
    >>> from stars.apps.accounts.mixins import PermMixin
    >>> from stars.apps.institutions.models import StarsAccount, Institution
    >>> from django.contrib.auth.models import User, AnonymousUser
    >>> from dummy_request import DummyRequest
         
    # Define a custom `BaseClass` for use with the mixin
    >>> class BaseClass(object):
    ...     def __call__(self, request, *args, **kwargs):
    ...         print "Hello World!"
    
    # Dummy user and StarsAccount
    >>> anon = AnonymousUser()
    >>> u = User.objects.create_user('testuser', 'test@example.com', 'testpw')
    >>> i = Institution(name='Fake Institution', aashe_id='-1')
    >>> i.save()
    >>> account = StarsAccount(institution=i, terms_of_service=True, user_level='submit', user=u)
    >>> account.save()
    >>> u.account = account
    
    # Dummy Request object
    >>> request = DummyRequest(anon)
         
    # User isn't authenticated should result in a redirect
    
    >>> class SubClass(PermMixin, BaseClass):
    ...     pass
    >>> sc = SubClass()
    >>> sc(request)
    <django.http.HttpResponseRedirect object at ...
    
    # Authenticated Users
    
    # Class doesn't define perm_list and should raise a permission denied error
    
    >>> request = DummyRequest(u)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e
    Permission Denied
    
    # ... using a custom error message
    
    >>> class SubClass(PermMixin, BaseClass):
    ...     perm_message = "This is a message"
    >>> request = DummyRequest(u)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e
    This is a message
    
    # Class defines perm_list and user doesn't have that permission ... permission denied
    >>> class SubClass(PermMixin, BaseClass):
    ...     perm_list = ['admin',]
    >>> request = DummyRequest(u)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e
    Permission Denied
    
    # Class defines perm_list and user has appropriate permission ... `__call__` executed
    >>> class SubClass(PermMixin, BaseClass):
    ...     perm_list = ['submit',]
    >>> request = DummyRequest(u)
    >>> sc = SubClass()
    >>> sc(request)
    Hello World!
    
"""
