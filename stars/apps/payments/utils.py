import re

def is_canadian_zipcode(zipcode):
    """
        Validates a Canadian zip code
    """
    pattern = "^[a-zA-Z]\d[a-zA-Z][ -]*\d[a-zA-Z]\d$"
    return bool(re.match(pattern, zipcode))


def is_usa_zipcode(zipcode):
    """
        Validates a USA zip code
    """
    pattern = "^\d\d\d\d\d$"
    return bool(re.match(pattern, zipcode))