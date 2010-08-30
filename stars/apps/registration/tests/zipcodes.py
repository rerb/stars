"""
    Doctests to test the zipcodecode validation in utils.py
    
    
    >>> from stars.apps.registration.utils import is_canadian_zipcode, is_usa_zipcode
    >>> is_canadian_zipcode("A0A 0A0")
    True
    >>> is_canadian_zipcode("a0a 0a0")
    True
    >>> is_canadian_zipcode("AAA 0A0")
    False
    >>> is_canadian_zipcode("AA 0A0")
    False
    >>> is_canadian_zipcode("A0A0A0")
    True
    >>> is_canadian_zipcode("A0A     0A0")
    True
    >>> is_canadian_zipcode("A0A-0A0")
    True
    >>> is_canadian_zipcode("A0A*0A0")
    False
    
    >>> is_usa_zipcode("02903")
    True
    >>> is_usa_zipcode("2903")
    False
    >>> is_usa_zipcode("a2903")
    False
    >>> is_usa_zipcode("00000")
    True
"""
