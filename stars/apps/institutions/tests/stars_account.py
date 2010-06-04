"""
    Test Suite for Institutions and StarsAccounts.  
    
   # Basic doctest for selecting StarsAccounts...

    >>> from stars.apps.institutions.models import StarsAccount, Institution
    >>> from django.contrib.auth.models import User
    >>> 
    >>> bob = User(username="bob", password="x")
    >>> bob.save()
    >>> uv = Institution(aashe_id='-1', name='UV')
    >>> uv.save()
    >>> aashe = Institution(aashe_id='-2', name='AASHE')
    >>> aashe.save()
    >>> a = StarsAccount(user=bob, institution=uv)
    >>> a.save()
    >>> b = StarsAccount(user=bob, institution=aashe)
    >>> b.save()
    >>> a.user == b.user
    True
    >>>    
    >>> a.select()
    >>> c = StarsAccount.objects.get(user=bob, institution=uv)
    >>> d = StarsAccount.objects.get(user=bob, institution=aashe)
    >>> c.is_selected
    True
    >>> d.is_selected
    False
    >>> StarsAccount.get_selected_account(bob) == a
    True
    >>>    
    >>> b.select()
    >>> c = StarsAccount.objects.get(user=bob, institution=uv)
    >>> d = StarsAccount.objects.get(user=bob, institution=aashe)
    >>> c.is_selected
    False
    >>> d.is_selected
    True
    >>> StarsAccount.get_selected_account(bob) == b
    True
    >>>    
    >>> b.deselect()
    >>> StarsAccount.get_selected_account(bob)
    >>> 
    >>> a.delete()
    >>> b.delete()
    >>> bob.delete()

"""
