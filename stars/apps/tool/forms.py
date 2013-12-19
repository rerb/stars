import django.forms

from stars.apps.helpers.forms.forms import LocalizedModelFormMixin
from stars.apps.institutions.models import Institution


class SettingsUpdateForm(LocalizedModelFormMixin):
    """
        A Form to update Settings.

        For now, there's only one setting, prefers_metric_system, stored
        on Institution.
    """
    prefers_metric_system = django.forms.BooleanField(
        label="Use metric system", required=False)

    class Meta:
        model = Institution
        fields = ['prefers_metric_system']

