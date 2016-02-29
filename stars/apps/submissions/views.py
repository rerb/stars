from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from stars.apps.credits.views import CreditsetStructureMixin
from stars.apps.submissions.forms import CreditSubmissionStatusUpdateForm
from stars.apps.submissions.models import (CreditUserSubmission,
                                           DocumentationFieldSubmission)


import re


class SubmissionStructureMixin(CreditsetStructureMixin):
    """
        Extends the creditset structure to work with SubmissionSets

        URL structure can be one of the following
            /institution_slug/submissionset/category_abbreviation/subcategory_slug/credit_number/

            <submissionset> can be either an ID or a date (####-##-##)
    """

    def update_context_callbacks(self):
        super(SubmissionStructureMixin, self).update_context_callbacks()
        self.add_context_callback("get_submissionset")
        self.add_context_callback("get_categorysubmission")
        self.add_context_callback("get_subcategorysubmission")
        self.add_context_callback("get_creditsubmission")
        self.add_context_callback("get_fieldsubmission")

    def get_object_list(self):
        """
            Returns a list of objects to use as filters for get_obj_or_call
        """
        return self.get_institution().submissionset_set.all()

    def get_submissionset(self, use_cache=True):
        """
            Attempts to get a submissionset using the kwargs.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        property = 'pk'
        pattern = "\d{4}-\d{2}-\d{2}"
        if re.match(pattern, self.kwargs['submissionset']):
            property = 'date_submitted'

        return self.get_obj_or_call(
            cache_key='submissionset',
            kwargs_key='submissionset',
            klass=self.get_object_list(),
            property=property,
            use_cache=use_cache
        )

    def get_creditset(self):
        """
            override get_creditset to extract from submissionset
        """
        if self.get_submissionset():
            return self.get_submissionset().creditset

    def get_categorysubmission(self):
        """
            Attempts to get a categorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_submissionset():
            return self.get_obj_or_call(
                cache_key='category_submission',
                kwargs_key="category_abbreviation",
                klass=self.get_submissionset().categorysubmission_set.all(),
                property='category__abbreviation'
            )

    def get_subcategorysubmission(self):
        """
            Attempts to get a subcategorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_categorysubmission():
            return self.get_obj_or_call(
                cache_key='subcategory_submission',
                kwargs_key="subcategory_slug",
                klass=self.get_categorysubmission().subcategorysubmission_set.all(),
                property='subcategory__slug'
            )

    def get_creditsubmission(self):
        """
            Attempts to get a creditusersubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_subcategorysubmission():
            return self.get_obj_or_call(
                cache_key='credit_submission',
                kwargs_key="credit_identifier",
                klass=self.get_subcategorysubmission().creditusersubmission_set.all(),
                property='credit__identifier'
            )

    def get_fieldsubmission(self):
        """
            Attempts to get a submission field.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        cache_key = "field_submission"
        obj = self.get_structure_object(cache_key)

        if not obj and self.get_creditsubmission() and self.get_field():
            klass = DocumentationFieldSubmission.get_field_class(
                self.get_field())
            obj = get_object_or_404(
                klass,
                documentation_field=self.get_field(),
                credit_submission=self.get_creditsubmission())
            self.set_structure_object(cache_key, obj)
        return obj


class CreditSubmissionStatusUpdateView(UpdateView):

    model = CreditUserSubmission
    form_class = CreditSubmissionStatusUpdateForm
    template_name = 'institutions/credit_submission_status_update.html'

    def get_object(self, *args, **kwargs):
        return CreditUserSubmission.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        import ipdb; ipdb.set_trace()
        credit_user_submission = self.get_object(commit=False)
        # recalculate credit score, submission set score
