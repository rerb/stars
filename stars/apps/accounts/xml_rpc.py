from django.conf import settings
from django.contrib.auth.models import User

import re

from stars.apps.helpers.xml_rpc import run_rpc
from stars.apps.accounts.models import UserProfile

def connect():
    
    return run_rpc('system.connect', ())

def logout():
    connect_response = connect()
    args = ()
    return run_rpc('aasheuser.logout', args, sessid=connect_response['sessid'])

def login(username, password):
    """
        Log a user in and return the dictionary of values returned by Drupal or None
    """
#    logout()
    connect_response = connect()
    args = (username, password)
    return run_rpc('aasheuser.login', args, sessid=connect_response['sessid'])
    
def get_user_by_email(email):
    """
        Query drupal through XML-RPC getbyemail with an email address and return a user dict or None
    """
    connect_response = connect()
    args = (email,)
    
    return run_rpc('aasheuser.getbyemail', args, sessid=connect_response['sessid'])
    
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
            
    # apply the MEMBER role if necessary
    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user, is_member=False)
    
    if user_dict['roles'].has_key('5'):
        # if they have the stars_admin role grant them staff access
        if not profile.is_member:
            profile.is_member = True
    else:
        # remove member status if they no longer have the role
        if profile.is_member:
            profile.is_member = False
    
    # list of associated institutions
    profile.profile_instlist = user_dict['profile_instlist']
    
    profile.save()
    
    return user