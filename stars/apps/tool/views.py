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
        context['rating_list'] = self.get_institution().submissionset_set.filter(
            status='r').filter(is_visible=True).order_by('date_submitted')
        return context
