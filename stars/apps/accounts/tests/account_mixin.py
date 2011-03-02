"""
    Account Mixin Doctests
    
    Test Premises:
     - AccountMixin:
      - no current institution
      - current institution isn't enabled
         
    >>> from stars.apps.accounts.mixins import AccountMixin
    >>> from stars.apps.institutions.models import StarsAccount, Institution
    >>> from django.contrib.auth.models import User, AnonymousUser
    >>> from dummy_request import DummyRequest
         
    # Define a custom `BaseClass` for use with the mixin
    >>> class BaseClass(object):
    ...     def __call__(self, request, *args, **kwargs):
    ...         print "Hello World!"
    
    >>> class SubClass(AccountMixin, BaseClass):
    ...     pass
    
    # No Institution
    
    >>> i = Institution(name='Fake Institution', aashe_id='-111', enabled=False)
    >>> i.save()
    
    # non-staff should return "Permission Denied"
    
    >>> anon = AnonymousUser()
    >>> anon.current_inst = None
    >>> anon.account_list = []
    >>> request = DummyRequest(anon)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e.__class__.__name__
    PermissionDenied
    
    # Available accounts should redirect to tool
    >>> anon.account_list = ["account",]
    >>> request = DummyRequest(anon)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e.__class__.__name__
    <django.http.HttpResponseRedirect object at ...
    
    # Staff should get a redirect
    >>> anon.is_staff = True
    >>> request = DummyRequest(anon)
    >>> sc = SubClass()
    >>> sc(request)
    <django.http.HttpResponseRedirect object at ...
    
    # institution disabled
    >>> anon.current_inst = i
    >>> request = DummyRequest(anon)
    >>> sc = SubClass()
    >>> try:
    ...     sc(request)
    ... except Exception, e:
    ...     print e.__class__.__name__
    PermissionDenied
    

    
"""
