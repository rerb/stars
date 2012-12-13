from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views.generic import ListView, RedirectView, TemplateView

from stars.apps.institutions.models import Institution, StarsAccount
from stars.apps.tool.mixins import InstitutionToolMixin


class SummaryToolView(InstitutionToolMixin,
                      TemplateView):
    """
        Displays the summary tool page for an institution.
    """
    tab_content_title = 'summary'
    template_name = 'tool/summary.html'

    def update_logical_rules(self):
        super(SummaryToolView, self).update_logical_rules()
        self.add_logical_rule({ 'name': 'user_has_view_access',
                                'param_callbacks': [
                                    ('user', 'get_request_user'),
                                    ('institution', 'get_institution')] })

    def get_context_data(self, **kwargs):
        context = super(SummaryToolView, self).get_context_data(**kwargs)
        context['rating_list'] = (
            self.get_institution().submissionset_set.filter(
            status='r').filter(is_visible=True).order_by('date_submitted'))
        return context

    def get(self, request, *args, **kwargs):
        # Since this is an InstitutionToolMixin, it assumes
        # kwargs['institution_slug'] can identify an Institution.
        # That might not be the case, since there might not be any
        # institution associated with request.user -- it can happen --
        # for instance, when any user registered w/aashe.org but not
        # stars.aashe.org goes to http://stars.aashe.org.  In these
        # cases, the institution_slug will be blank, and we want to
        # show the "you should really register for STARS" message.
        if kwargs['institution_slug'].strip() == '':
            error_msg = """
                Your AASHE Account is not verified to access the STARS
                Reporting Tool.  Only institutions that are registered
                as STARS Participants are able to access the Reporting
                Tool.  You may be receiving this message because you
                have not been listed as a user by the account's
                administrator.  The administrator is likely to be the
                person who first registered for STARS or your
                institution's STARS Liaison.  Please contact that
                person so they may list you as a user in the Reporting
                Tool and you may gain access.  <br/><br/> To add
                users, once the administrator is logged into the
                Reporting Tool, simply choose the "My Summary" link on
                the left, then click on the "Users" tab.
                """
            raise PermissionDenied(error_msg)
        else:
            return super(SummaryToolView, self).get(request, *args, **kwargs)


class ToolLandingPageView(RedirectView):
    """
        Redirects user based on the number of STARS accounts he's
        associated with.  Probably mis-named; not really a landing page,
        in that no one ever actually lands here.

        Provides a view that can be pointed to by the 'Reporting' link
        in the menu nav and bread crumbs.
    """

    def get_redirect_url(self, **kwargs):
        """
        Redirect based on the number of STARS accounts associated with
        this user.
        """
        stars_accounts = StarsAccount.objects.filter(user=self.request.user)

        if stars_accounts.count() is 0:
            return reverse('no-stars-account')
        elif stars_accounts.count() is 1:
            return reverse('tool-summary', stars_accounts[0].institution.slug)
        else:
            return reverse('select-institution')


class NoStarsAccountView(TemplateView):
    """
        Explains to a user what it means that he has no STARS account.

        Needed because folks w/AASHE accounts can get to STARS, but
        are not allowed to access to the reporting tool.
    """
    template_name = 'tool/no_stars_account.html'

    def get_context_data(self, **kwargs):
        context = super(NoStarsAccountView, self).get_context_data(**kwargs)
        institution = self.get_institution(user=self.request.user)
        context['institution'] = institution
        context['liaison_name'] = self.get_liaison_name(institution)
        context['liaison_phone'] = self.get_liaison_phone(institution)
        context['liaison_email'] = (institution.contact_email if institution
                                    else None)
        return context

    def get_institution(self, user):
        """
            Returns one institution associated with this user.

            Usually this is the only institution associated with
            this user.  Rarely, more than one institution will be
            associated with a user; when this happens, the first
            institution that's a STARS participant will be returned.
        """
        if not user.userprofile.profile_instlist:
            return None

        institution_ids = user.userprofile.profile_instlist.split(',')
        num_institutions = len(institution_ids)

        # profile_instlist can be empty, so:
        if num_institutions is 0:
            institution = None
        elif num_institutions is 1:
            try:
                institution = Institution.objects.get(id=institution_ids[0])
            except Institution.DoesNotExist:
                institution = None
        else:
            # valid_institution_ids is a list of ids that point to
            # Institutions; keep track of them so that, in the event that
            # none of the institution_ids represent an Institution that's
            # a STARS participant, we don't try to lookup an id that
            # doesn't point to an Institution.
            valid_institution_ids = []
            for institution_id in institution_ids:
                try:
                    institution = Institution.objects.get(id=institution_id)
                    valid_institution_ids.append(institution.id)
                    if institution.is_participant:
                        break
                except Institution.DoesNotExist:
                    next
            else:
                # None are STARS participants? Just return the first one.
                if valid_institution_ids:
                    institution = Institution.objects.get(
                        id=valid_institution_ids[0])
                else:  # lookup failed for all institution_ids
                    institution = None

        return institution

    def get_liaison_name(self, institution):
        if institution:
            full_name = ''
            for name in (institution.contact_first_name,
                         institution.contact_middle_name,
                         institution.contact_last_name):
                if name:
                    full_name += name + ' '
            return full_name.strip()
        else:
            return None

    def get_liaison_phone(self, institution):
        if institution:
            if institution.contact_phone:
                if institution.contact_phone_ext:
                    return '{phone} x{ext}'.format(
                        phone=institution.contact_phone,
                        ext=institution.contact_phone_ext)
                else:
                    return institution.contact_phone
            else:
                return None
        else:
            return None


class SelectInstitutionView(ListView):
    """
        Displays a list of institutions this user has a STARS account for.

        When a user selects an institution, he's redirected to the
        tool-summary page for that institution.
    """
    model = StarsAccount
    tab_content_title = 'institutions'
    template_name = 'tool/select_institution.html'

    def get_queryset(self):
        return StarsAccount.objects.filter(user=self.request.user).order_by(
            'institution__name')
