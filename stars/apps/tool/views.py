from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView

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
