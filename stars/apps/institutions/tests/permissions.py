"""
    StarsAccount Permissions Doctests

    Test Premises:
     - `has_access_level` applies permissions correctly
    
    >>> from stars.apps.institutions.models import StarsAccount, Institution
    >>> from django.contrib.auth.models import User
     
    >>> bob = User(username="bob", password="x")
    >>> bob.save()
    >>> uv = Institution(aashe_id='-1', name='UV')
    >>> uv.save()
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