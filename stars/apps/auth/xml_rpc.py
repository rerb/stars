from django.conf import settings
from django.contrib.auth.models import User

import re

from stars.apps.helpers.xml_rpc import run_rpc
    
def login(username, password):
    """
        Log a user in and return the dictionary of values returned by Drupal or None
    """
    args = (username, password)
    return run_rpc('aasheuser.login', args)
    
def get_user_by_email(email):
    """
        Query drupal through XML-RPC getbyemail with an email address and return a user dict or None
    """
    args = (email,)
    return run_rpc('aasheuser.getbyemail', args)
    
def get_user(uid):
    """
        Query drupal through XML-RPC getuser with a user id and return a user dict or None
    """
    args = (uid,)
    return run_rpc('aasheuser.get', args)

def email_to_username(email):
    """
        Converts an email address to a valid django username
        Keep in mind that they still need to be unique
    """
    username = email.replace('@', "__").replace('.', "_").replace('-', '_')
    if len(username) > 30:
        username = username[0:30]
    return username
    
def get_user_from_user_dict(user_dict, session, create=True):
    """
        Returns a User object when given a dict (returned from drupal)
        if the user does not exist, it will be created (if indicated)
    """
    if session:
        password = session
    else:
        password = user_dict['pass']
    try:
        user = User.objects.get(id=int(user_dict['uid']))
        if user.email != user_dict['mail']:
            user.email = user_dict['mail']
            user.username = email_to_username(user_dict['mail'])
        user.password = password
        user.first_name = user_dict['profile_fname']
        user.last_name = user_dict['profile_lname']
    except User.DoesNotExist:
        if not create:
            return None
        # Create a new user.
        # We set the password to the current sessid
        # it is never checked
        
        user = User(username=email_to_username(user_dict['mail']), email=user_dict['mail'], id=user_dict['uid'], password=password)
    user.save()
    # Note: if User record was created from different SSO server, uid could be out of sync with User.id. 
    #       In this case, save() will cause an integrity check error.  See http://code.aashedev.org/stars/ticket/129

    # apply the appropriate permissions
    # @TODO: take a look at this...  We could use the role name, 'stars_admin' instead?
    if user_dict['roles'].has_key('9'):
        # if they have the stars_admin role grant them staff access
        if not user.is_staff:
            user.is_staff = True
            user.is_superuser = True
            user.save()
    else:
        # remove admin status if they no longer have the role
        if user.is_staff:
            user.is_staff = False
            user.is_superuser = False
            user.save()
    return user
