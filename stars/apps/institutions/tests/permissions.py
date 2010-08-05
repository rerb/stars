"""
    StarsAccount Permissions Doctests

    Test Premises:
     - `has_access_level` applies permissions correctly

    >>> from django.core import management
    >>> from stars.apps.institutions.models import StarsAccount, Institution
    >>> from django.contrib.auth.models import User
    >>> management.call_command("flush", verbosity=0, interactive=False)
    >>> management.call_command("loaddata", "institutions_testdata.json", verbosity=0)

    >>> bob = User.objects.get(pk=1)
    >>> uv = Institution.objects.get(pk=1)
    >>> a = StarsAccount(user=bob, institution=uv, user_level='view', terms_of_service=True)
    >>> a.save()

    >>> a.has_access_level('admin')
    False
    >>> a.has_access_level('submit')
    False
    >>> a.has_access_level('view')
    True

    >>> a.user_level = 'submit'
    >>> a.save()

    >>> a.has_access_level('admin')
    False
    >>> a.has_access_level('submit')
    True
    >>> a.has_access_level('view')
    True
    
    >>> a.user_level = 'admin'
    >>> a.save()
    
    >>> a.has_access_level('admin')
    True
    >>> a.has_access_level('submit')
    True
    >>> a.has_access_level('view')
    True
"""
