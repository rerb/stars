"""
    Doctest to check PendingAccounts
    
    Test premises:
        - Pending accounts can be converted to STARS accounts when account exists
        - Email doesn't have to have the same case

    >>> from django.core import management
    >>> from stars.apps.institutions.models import PendingAccount, StarsAccount, Institution
    >>> from django.contrib.auth.models import User
    >>> management.call_command("flush", verbosity=0, interactive=False)
    >>> management.call_command("loaddata", "institutions_testdata.json", verbosity=0)

    >>> i = Institution.objects.get(pk=1)
    >>> user = User.objects.get(pk=1)
    
    >>> pa = PendingAccount(user_email='bob@testdomain.org', institution=i)
    >>> pa.save()
    
    >>> account = pa.convert_accounts(user)
    >>> print account.__class__.__name__
    StarsAccount
    >>> account.delete()
    
    # Testing case sensitivity
    >>> pa = PendingAccount(user_email='BOB@TestDomain.ORG', institution=i)
    >>> pa.save()
    
    >>> account = pa.convert_accounts(user)
    >>> print account.__class__.__name__
    StarsAccount
    >>> account.delete()

"""
