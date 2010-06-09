"""
    Doctest to check PendingAccounts
    
    Test premises:
        - Pending accounts can be converted to STARS accounts when account exists
        - Email doesn't have to have the same case
        
    >>> from stars.apps.institutions.models import PendingAccount, StarsAccount, Institution
    >>> from django.contrib.auth.models import User
    
    >>> i = Institution(name='Institution', aashe_id='-1')
    >>> i.save()
    >>> user = User(username="bob", password="x", email='bob@testdomain.org')
    >>> user.save()
    >>> pa = PendingAccount(user_email='bob@testdomain.org', institution=i)
    >>> pa.save()
    
    >>> account = pa.convert_accounts(user)
    >>> print account.__class__.__name__
    StarsAccount
    
    # Testing case sensitivity
    >>> pa = PendingAccount(user_email='BOB@TestDomain.ORG', institution=i)
    >>> pa.save()
    
    >>> account = pa.convert_accounts(user)
    >>> print account.__class__.__name__
    StarsAccount

"""