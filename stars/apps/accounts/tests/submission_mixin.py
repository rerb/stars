"""
    Submission Mixin Doctests
    
    Test Premises:
     - SubmissionMixin
      - no active submission
      - active submission hasn't been enabled
         
    >>> from stars.apps.accounts.mixins import SubmissionMixin
    >>> from stars.apps.institutions.models import StarsAccount, Institution, InstitutionState
    >>> from stars.apps.credits.models import CreditSet
    >>> from stars.apps.submissions.models import SubmissionSet, Payment
    >>> from django.contrib.auth.models import User
    >>> from dummy_request import DummyRequest
    >>> from datetime import datetime
         
    # Define a custom `BaseClass` for use with the mixin
    >>> class BaseClass(object):
    ...     def __call__(self, request, *args, **kwargs):
    ...         print "Hello World!"
    
    >>> class SubClass(SubmissionMixin, BaseClass):
    ...     pass
    
    >>> i = Institution(name='Fake Institution', aashe_id='-11', enabled=True)
    >>> i.save()
    >>> cs = CreditSet(version='100', release_date=datetime.now(), tier_2_points='.25', is_locked=False)
    >>> cs.save()
    >>> u = User.objects.create_user('s_testuser', 'test@example.com', 'testpw')
    >>> u.current_inst = i
    >>> u.account_list = []
    >>> u.save()
    >>> account = StarsAccount(institution=i, terms_of_service=True, user_level='admin', user=u)
    >>> account.save()
    >>> u.account = account
    >>> u.save()
    >>> ss = SubmissionSet(creditset=cs, institution=i, date_registered=datetime.now(), registering_user=u)
    >>> ss.save()
    
    # No Active Submission
    # User is staff: redirect
    >>> u.is_staff = True
    >>> request = DummyRequest(u)
    >>> sc = SubClass()
    >>> sc(request)
    <django.http.HttpResponseRedirect object at ...
    
    # User is just an admin: redirect
    >>> u.is_staff = False
    >>> sc(request)
    <django.http.HttpResponseRedirect object at ...
    
    # User can only submit: permission denied
    >>> account.user_level = 'submit'
    >>> try:
    ...  sc(request)
    ... except Exception, e:
    ...  print e.__class__.__name__
    PermissionDenied
    
    # Active submission is disabled: permission denied
    >>> i.current_submission = ss
    >>> i.save()
    >>> ss.is_enabled()
    False
    >>> try:
    ...  sc(request)
    ... except Exception, e:
    ...  print e.__class__.__name__
    PermissionDenied
    
    # Active Submission exists
    >>> p = Payment(submissionset=ss, type='check', date=datetime.now(), amount='0', user=u)
    >>> p.save()
    >>> ss.is_enabled()
    True
    >>> sc(request)
    Hello World!
    
"""
