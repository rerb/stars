from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django.contrib.localflavor.us.models import PhoneNumberField

class Institution(models.Model):
    """
        This model represents a STARS institution. The institution name
        is a mirror of Drupal and will require regular updating
    """
    name = models.CharField(max_length='255')
    aashe_id = models.IntegerField()
    enabled = models.BooleanField(help_text="This is a staff-only flag for disabling an institution. An institution will NOT appear on the STARS Institutions list until it is enabled. ")
    contact_first_name = models.CharField(max_length=32)
    contact_middle_name = models.CharField(max_length=32, blank=True, null=True)
    contact_last_name = models.CharField(max_length=32)
    contact_title = models.CharField(max_length=64)
    contact_department = models.CharField(max_length=64)
    contact_phone = PhoneNumberField()
    contact_email = models.EmailField()
    executive_contact_first_name = models.CharField(max_length=32)
    executive_contact_middle_name = models.CharField(max_length=32, blank=True, null=True)
    executive_contact_last_name = models.CharField(max_length=32)
    executive_contact_title = models.CharField(max_length=64)
    executive_contact_department = models.CharField(max_length=64)
    executive_contact_email = models.EmailField()
    
    def __unicode__(self):
        return self.name
        
    def get_admin_url(self):
        """ Returns the URL for AASHE Staff to edit this institution """
        return "/dashboard/admin/institution/%d/" % self.aashe_id
        
    def get_manage_url(self):
        """ Returns the URL for institution admins to edit this institution """
        return "/dashboard/manage/"
        
    def get_state(self):
        """ Returns the InstitutionState object associated with this institution, or None
            - clients should generally access the more specific methods, like get_active_submission
        """
        try: 
            #@todo:  this patched only - see ticket #252  & test case in edit_submissionset view, line 164
            state = InstitutionState.objects.get(institution = self)
            return state
#            return self.state   ## related field can get out-of-sync with DB??? see ticket #252
        except InstitutionState.DoesNotExist:
            return None
        
    def get_active_submission(self):
        """ Returns the current SubmissionSet for this institution """
        try:
            return self.get_state().active_submission_set
        except Exception,e:
            return None
        
    def set_active_submission(self, submission_set):
        """ Set this institution's active SubmissionSet """
        state = self.get_state()
        if state is None:
            state = InstitutionState(institution=self, active_submission_set=submission_set)
        elif state.active_submission_set != submission_set:
            state.active_submission_set = submission_set
        state.save()

    @staticmethod
    def find_institutions(snippet):
        """
            Searches stars_member_list for any school that includes the snippet in its name
            returns a list of institutions, maybe empty.
        """
        return _query_member_list("""name like '%%%s%%'"""%snippet)
        
    def is_member_institution(self):
        """
            Searches stars_member_list.members for the institution
            returns True if this institution exists
        """        
        if _query_member_list("organization_id = %s AND is_member = TRUE"%self.aashe_id):
            return True
        return False
    
    @staticmethod
    def load_institution(aashe_id):
        """
            Connects to stars_member_list to update/create a local
            mirror of the requested institution
            Returns the institutions or None
        """
        # Get institution data from aashedata01
        result = _query_member_list("organization_id = %s"%aashe_id)
        
        institution = None
        if len(result): # If the institution is an active member...
            result_institution = result[0]
            try:       # check if the institution exists locally...
                institution = Institution.objects.get(aashe_id=aashe_id)
            except Institution.DoesNotExist:  # ... if not, create it
                institution = Institution(aashe_id=result_institution['id'], name=result_institution['name'], enabled=False)
                institution.save()
        else: # institution is not an aashe member...
            try: # disable non-member institution if it's saved locally
                institution = Institution.objects.get(aashe_id=aashe_id)
                institution.enabled = False
                institution.save()
            except Institution.DoesNotExist:  # how did we get here?
                pass
        return institution
    
def _query_member_list(where_clause):
    """
        PRIVATE: Searches stars_member_list.members table for schools that match to given where_clause
        Returns a list of institution dictionaries (id name), maybe empty.
    """
    from stars.apps.auth.utils import connect_member_list
    db = connect_member_list()
    cursor = db.cursor()
    query = """
        SELECT organization_id as id, name, city, state FROM `members`
        WHERE %s
        ORDER BY name""" % (where_clause)
    cursor.execute(query)
    institution_list = [{'id': row[0], 'name': row[1], 'city': row[2], 'state': row[3]} for row in cursor.fetchall()]

    db.close()
    return institution_list


class InstitutionState(models.Model):
    """
        Tracks the current state of an institution such as the current submission set
    """
    from stars.apps.submissions.models import SubmissionSet

    institution = models.OneToOneField(Institution, related_name='state')
    active_submission_set = models.ForeignKey(SubmissionSet)

    def __unicode__(self):
        return unicode(self.institution)
    

STARS_USERLEVEL_CHOICES = [(x, x) for x in settings.STARS_PERMISSIONS]

class StarsAccount(models.Model):
    """
        This Model associates users with institutions at different access levels
        Although the institutions field is d, clients should not assume it is always non-None (see DuckAccount below)
        Accounts serve permissions for users on institutuions -
          - PRIVATE: user_level should generally be treated as private
          - BEST PRACTICES: use request.user.has_perm( perm ) to check access rights!
    """
    # @todo: consider moving StarsAccount to stars auth?
    # @todo: user-institution should be a unique key in this table?
    user = models.ForeignKey(User)
    institution = models.ForeignKey(Institution)
    # user_level is a role
    user_level = models.CharField(max_length='6', choices=STARS_USERLEVEL_CHOICES)
    is_selected = models.BooleanField(default=False)  # True if the user has this account selected - we need this so we can persist the user's account on logout. 
    
    def __unicode__(self):
        return "%s" % self.user
    
    def get_edit_url(self):
        return settings.MANAGE_USERS_URL

    def get_delete_url(self):
        return "%sdelete/%s"%(settings.MANAGE_USERS_URL, self.id)

    def select(self):
        """
            Make this account the user's active account, and so de-select all of user's other accounts.
        """
        if not self.is_selected:
            for account in self.user.starsaccount_set.filter(is_selected=True):
                account.deselect()
            self.is_selected = True
            self.save()
        
    def deselect(self):
        """ 
            De-select this account, and persist the change.
        """
        self.is_selected = False
        self.save()
        
    @staticmethod
    def get_selected_account(user):
        """ 
            Return the account the given user currently has selected, or None 
            Ideally, this method would be part of the user object... but...
        """
        account = user.starsaccount_set.filter(is_selected=True)
        return account[0] if account else None  # there should only be one account selected at a time.
        
    def has_perm(self, perm):
        """ 
            Return True if this account grants user the given permission.
            CAREFUL: only checks permission - does not do complete access rights check.
            Clients should call request.user.has_perm(perm) to verify user access rights within current request context.
            - perm: One of settings.STARS_PERMISSIONS
        """
        return _has_perm(self, perm)

def _has_perm(account, perm):
    """ Helper so that StarsAccount and DuckAccount can share logic """
        # admin users can submit, otherwise permissions and roles are synonymous
    return perm=='submit' and account.user_level=='admin' or \
           perm == account.user_level


class DuckAccount(object):
    """
        If it walks like a StarsAccount, and quacks like a StarsAccount...
        Except:
            - DuckAccounts have no persistence, no DB backend, and no queries.
            - by default DuckAccounts have no permssions - they must be set explicitly
            - institution may be None.  CAREFUL - potential issues - clients of StarsAccount should not make that assumption!
        Why?
            - testing: useful to be able to create mock user accounts on the fly
            - staff:  don't have accounts, which may lead to special case logic.
            - reduced duplication: current_inst is currently duplicated in user and user.account - there may be other such cases in future
        This is not being used right now - it was just an idea I was toying with... may be useful in future.
    """
    def __init__(self, user, institution=None, user_level=None):
        self.user = user
        self.institution = institution
        self.user_level = user_level
        
    def __unicode__(self):
        return "%s (quack)"%self.user
   
    def has_perm(self, perm):
        return _has_perm(self, perm)


class AccountInvite(models.Model):
    """
        When an institution admin invites a user to join
    """