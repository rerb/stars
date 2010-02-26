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
    enabled = models.BooleanField(help_text="This is a staff-only flag for disabling an institution. An institution will NOT appear on the STARS Institutions list until it is enabled.", default=False)
    contact_first_name = models.CharField("Liaison First Name", max_length=32)
    contact_middle_name = models.CharField("Liaison Middle Name", max_length=32, blank=True, null=True)
    contact_last_name = models.CharField("Liaison Last Name", max_length=32)
    contact_title = models.CharField("Liaison Title", max_length=64)
    contact_department = models.CharField("Liaison Department", max_length=64)
    contact_phone = PhoneNumberField("Liaison Phone")
    contact_email = models.EmailField("Liaison Email")
    executive_contact_first_name = models.CharField(max_length=32)
    executive_contact_middle_name = models.CharField(max_length=32, blank=True, null=True)
    executive_contact_last_name = models.CharField(max_length=32)
    executive_contact_title = models.CharField(max_length=64)
    executive_contact_department = models.CharField(max_length=64)
    executive_contact_email = models.EmailField()
    charter_participant = models.BooleanField()
    
    def __unicode__(self):
        return self.name
        
    def get_admin_url(self):
        """ Returns the base URL for AASHE Staff to administer aspects of this institution """
        return "%sinstitution/%d/" % (settings.ADMIN_URL, self.id)
        
    def get_masquerade_url(self):
        """ Returns the URL for AASHE Staff to masquerade this institution """
        return "%sinstitution/masquerade/%d/" % (settings.ADMIN_URL, self.aashe_id)

    def get_manage_url(self):
        """ Returns the URL for institution admins to edit this institution """
        return settings.MANAGE_INSTITUTION_URL
            
    def get_admin_payments_url(self):
        """ Returns the URL for administering this institution's payments """
        return "%spayments/" % self.get_admin_url()

    def has_multiple_submissions(self):
        """ Return True if this institution has more than one submission set """
        return self.submissionset_set.count() > 1
    
    def get_submissions(self, include_unrated=False):
        """ Return the institutions SubmissionSets, reverse chron., perhaps excluding the unrated ones """
        submissions = self.submissionset_set.all()
        if not include_unrated:  # include only rated submissions
            submissions = submissions.filter(status='r')
        return submissions.order_by("-date_registered")

    def get_latest_submission(self, include_unrated=False):
        """ Return the institutions most recent SubmissionSet, perhaps excluding the unrated ones """
        try:
            return self.get_submissions(include_unrated)[0]
        except:
            return None
        
    def get_payments(self):
        """ Return the latest payment for this institution """
        payments = []
        for ss in self.submissionset_set.all():
            for p in ss.payment_set.all():
                payments.append(p)
        return payments
                    
    def get_active_submission(self):
        """ Returns the current SubmissionSet for this institution """
        try:
            return self.state.active_submission_set
        except Exception,e:
            return None
 
    def set_active_submission(self, submission_set):
        """ Set this institution's active SubmissionSet """
        try:
            if self.state.active_submission_set != submission_set:
                self.state.active_submission_set = submission_set
        except InstitutionState.DoesNotExist:
            self.state = InstitutionState(institution=self, active_submission_set=submission_set)
        
        self.state.save()

    def get_latest_rated_submission(self):
        """ Returns the most recent rated SubmissionSet for this institution """
        try:
            return self.state.latest_rated_submission_set
        except Exception,e:
            return None
 
    def set_latest_rated_submission(self):
        """ Update this institution's most recent rated SubmissionSet """
        latest_rated = self.get_latest_submission(include_unrated=False)
        if latest_rated is None:
            if self.state:
                self.state.latest_rated_submission_set = None
        else:
            if self.state is None:
                self.state = InstitutionState(institution=self, active_submission_set=latest_rated)
            elif self.state.latest_rated_submission_set != latest_rated:
                self.state.latest_rated_submission_set = latest_rated
        if self.state:
            self.state.save()

    def is_registered(self, creditset=None):
        """ 
            Return True iff this institution is registered for the given credit set 
            creditset - if None, the latest creditset will be checked.
        """
        if not creditset:
            from stars.apps.credits.models import CreditSet
            creditset = CreditSet.get_latest_creditset()
            
        for submission in self.submissionset_set.all():
            if submission.creditset == creditset:
                return True
        # assert: no submission has been registered for the given credit set for this institution
        return False
    
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
        if _query_member_list("account_num = '%s' AND is_member = 1"%self.aashe_id):
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
        result = _query_member_list("account_num = '%s'"%aashe_id)
        
        institution = None
        if len(result): # If the institution is an active member...
            result_institution = result[0]
            try:       # check if the institution exists locally...
                institution = Institution.objects.get(aashe_id=aashe_id)
            except Institution.DoesNotExist:  # ... if not, create it
                institution = Institution(aashe_id=result_institution['id'], name=result_institution['name'], enabled=False)
                # These institutions are disabled because they won't have been created through registration...
                institution.save()
        else: # institution is not in our ISS DB
            try: # disable non-member institution if it's saved locally
                institution = Institution.objects.get(aashe_id=aashe_id)
                # institution.enabled = False
                institution.save()
            except Institution.DoesNotExist:  # how did we get here?
                pass
        return institution
    
def _query_member_list(where_clause):
    """
        PRIVATE: Searches stars_member_list.members table for schools that match to given where_clause
        !!!!Assumes that where_clause has been properly sanitized and quoted!!!!
        Returns a list of institution dictionaries (id name), maybe empty.
    """
    from stars.apps.auth.utils import connect_member_list
    db = connect_member_list()
    cursor = db.cursor()
    query = """
        SELECT organization_id as id, name, city, state FROM `org_export`
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
    active_submission_set = models.ForeignKey(SubmissionSet, related_name='active_submission')
    latest_rated_submission_set = models.ForeignKey(SubmissionSet, related_name='rated_submission', null=True, blank=True, default=None)

    def __unicode__(self):
        return unicode(self.institution)


class InstitutionPreferences(models.Model):
    """
        Tracks preferences and site-wide settings for an institution.
        Every preference should have default value, and code that access prefernces
        should simply create a new prefernce model if one does not exist for an institution yet.
        Preferences can be re-set to default simply by deleting the preference model for an institution.
    """
    institution = models.OneToOneField(Institution, primary_key=True, related_name='preferences', editable=False)
    notify_users = models.BooleanField(default=True)
    

STARS_USERLEVEL_CHOICES = settings.STARS_PERMISSIONS

class BaseAccount(models.Model):
    """
        A 'multi-table inheritance' base class - ensures all accounts have unique id's.
        This is important because the different kinds of Accounts are mixed together in lists and
        so must have uniuqe id's between them so their id's uniquely identify them in the list.
        Multi-table inheritance is a way of ensuring that each child class record has a unique id.
    """
    pass

class AbstractAccount(BaseAccount):
    """
        Abstract base class for StarsAccount and Pendingccount.
        Logically, this stuff could go in the BaseAccount class, but there are 2 reasons to use an Abstract base class here:
        1) so that the reverse relation, institution.starsaccount_set, works
        2) so that unique_together constraints can be handled by Django
    """
    institution = models.ForeignKey(Institution)
    terms_of_service = models.BooleanField()
    # user_level is a role
    user_level = models.CharField("Role", max_length='6', choices=STARS_USERLEVEL_CHOICES)

    class Meta:
        abstract = True

    @classmethod
    def get_manage_url(cls):
        return settings.MANAGE_USERS_URL

    def get_edit_url(self):
        return "%sedit/%s/"%(settings.MANAGE_USERS_URL, self.id)

    def get_delete_url(self):
        return "%sdelete/%s/"%(settings.MANAGE_USERS_URL, self.id)

    def is_pending(self):
        return False

    def last_access(self):
        """
            Return the date of the last access to this account, or None
            Currently, this just uses the date of user's last login to STARS.
        """
        # HACK alert - Django stores a default of now() in last_login field when account is created.
        #            - as a result, last_login < date_joined when user hasn't logged in yet.
        #  - seems a bit fragile, but that's really the only way I can think of to determine if user has not logged in yet...
        if self.is_pending():
            return None
        last_login = self.user.last_login.replace(microsecond=0)
        date_joined = self.user.date_joined.replace(microsecond=0)
        return None if (self.user.last_login < self.user.date_joined) else self.user.last_login
    
    # Each action below corresponds to an e-mail template for a notification message
    NEW_ACCOUNT='new_account.txt'
    CHANGE_ROLE='change_role.txt'
    DELETE_ACCOUNT='delete_account.txt'
    def get_formatted_message(self, action, admin, institution):
        """
            Format an e-mail message with the information from this entry
        """
        from django.template.loader import render_to_string
        template = "tool/manage/emails/%s"%action
        context = {'account': self, 'admin':admin, 'institution':institution}
        return render_to_string(template, context)

    def notify(self, action, admin, institution):
        """ 
            Notify account holder about an action taken on their account 
            action must be one of the action constants defined by this class above
        """
        if not settings.DEBUG:
            from django.core.mail import send_mail
            send_mail('STARS Account notification for: %s'%self.user, \
                      self.get_formatted_message(action, admin, institution),  \
                      settings.EMAIL_HOST_USER, [self.user.email], fail_silently=True )
        else:
            print "Account Notification: E-mail would have been sent to %s:"%self.user.email
            print self.get_formatted_message(action, admin, institution)
            
    @classmethod
    def update_account(cls, admin, notify_user, institution, user_level, **user_params):
        """ 
            Create or update an account 
            admin is the user who is doing the update - used for notifying user of account change.
            user_params are passed through to cls to uniquely identify or create account.
            returns the updated or newly created account.
        """
        has_changed = True
        is_create = False
        try:
            # See if there is already a  Account for this user
            account = cls.objects.get(institution=institution, **user_params)
            if account.user_level != user_level:
                account.user_level = user_level
            else:
                has_changed = False
        except cls.DoesNotExist:
            # Or create one
            account = cls(institution=institution, user_level=user_level, **user_params)
            is_create = True
        account.save()
        
        # Notify the user only if something actually changes AND admin wanted to notify them.
        if has_changed and notify_user:
            action = StarsAccount.NEW_ACCOUNT if is_create else StarsAccount.CHANGE_ROLE
            account.notify(action, admin, institution)
            
        return account


class StarsAccount(AbstractAccount):
    """
        This Model associates users with institutions at different access levels
        Although the institutions field is d, clients should not assume it is always non-None (see DuckAccount below)
        Accounts serve permissions for users on institutuions -
          - PRIVATE: user_level should generally be treated as private
          - BEST PRACTICES: use request.user.has_perm( perm ) to check access rights!
    """
    user = models.ForeignKey(User)
    is_selected = models.BooleanField(default=False)  # True if the user has this account selected - we need this so we can persist the user's account on logout. 

    class Meta:
        unique_together = ("user", "institution")
    
    def __unicode__(self):
        return "%s" % self.user
    
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
        # anyone with an account can view, admin users can submit, otherwise permissions and roles are synonymous
    return perm=='view' or \
           (perm=='submit' and account.user_level=='admin') or \
           perm == account.user_level


class PendingAccount(AbstractAccount):
    """
        Represents a StarsAccount for a 'user' without an IRC account.
        Since there is no way to create a User object for them, they can't have an StarsAccount,
        so we create a PendingAccount and convert it to a StarsAccount on their first login.
        All the logic around PendingAccounts assumes:
          - PendingAccounts are only ever created for users without AASHE accounts
          - the first time the user logs in to STARS, all PendingAccounts are converted to StarsAccounts
    """
    user_email = models.EmailField()

    class Meta:
        unique_together = ("user_email", "institution")
    
    def __unicode__(self):
        return "%s" % self.user_email
    
    def is_pending(self):
        return True

    def _get_user(self):
        """ 
            Clients want to treat self as if it were a StarsAccount, which has a User field.
              so we need to fulfill calls to account.user.x
            So, we create a DuckUser, which (hopefully) supplies all the methods clients will call on!
        """
        return DuckUser(self.user_email)
    user = property(_get_user, )

    @staticmethod
    def convert_accounts(user):
        """
            Convert to StarsAccounts any accounts pending for the given user.
            If any accounts are converted, one is selected and returned,
            otherwise, if the user has no pending accounts, returns None.
        """
        pending_accounts = PendingAccount.objects.filter(user_email=user.email)
        account = None
        for pending in pending_accounts:  # seems unlikely there will be more than 1, but it could happen...
            account = StarsAccount(user=user, institution=pending.institution, user_level=pending.user_level)
            account.save()
            pending.delete()
                        
        if account:  # selected account will be the last account converted
            account.select()
        return account


class DuckUser(object):
    """
        If it waddles like a User, and quacks like a User...
        Except:
            - DuckUsers have no persistence, no DB backend, and no queries.
            - DuckUsers have a very limited set of capabilities - just enough to satisfy our current needs.
        Why?
            - to satisfy the needs of PendingAccount
     """
    def __init__(self, user_email):
        self.email = user_email
        
    def __str__(self):
        return "%s" % self.email
    
    def get_full_name(self):
        return self.__str__()
       
    
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
        
    def __str__(self):
        return "%s (quack)"%self.user
   
    def has_perm(self, perm):
        return _has_perm(self, perm)


class AccountInvite(models.Model):
    """
        When an institution admin invites a user to join
    """
