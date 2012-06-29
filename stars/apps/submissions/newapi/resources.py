"""
    STARS Submissions API
"""
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.http import HttpGone, HttpMultipleChoices

from stars.apps.credits.models import Category, Credit, Subcategory
from stars.apps.submissions.models import SubmissionSet, CategorySubmission, \
     SubcategorySubmission, CreditUserSubmission, NumericSubmission, \
     TextSubmission, LongTextSubmission, URLSubmission, DateSubmission, \
     UploadSubmission, BooleanSubmission, ChoiceSubmission, \
     MultiChoiceSubmission
from stars.apps.api.resources import StarsApiResource
from stars.apps.api.paths import CREDITS_RESOURCE_PATH, \
     SUBMISSIONS_RESOURCE_PATH, INSTITUTIONS_RESOURCE_PATH


class SubmissionSetResource(StarsApiResource):
    """
        Resource for accessing any (published) SubmissionSet.
    """
    creditset = fields.OneToOneField(
        CREDITS_RESOURCE_PATH + 'CreditSetResource', 'creditset')
    categories = fields.ToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'CategorySubmissionResource',
        'categorysubmission_set')
    institution = fields.OneToOneField(
        INSTITUTIONS_RESOURCE_PATH + 'InstitutionResource', 'institution')
    rating = fields.CharField(readonly=True)

    class Meta(StarsApiResource.Meta):
        queryset = SubmissionSet.objects.published()
        resource_name = 'submissions'
        allowed_methods = ['get']
        # exclude submission_boundary becauses it raises
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = [
            'is_locked',
            'is_visible',
            'date_reviewed',
            'date_registered',
            'status',
            ]

    def dehydrate_rating(self, bundle):
        if bundle.data['rating']:
            return bundle.data['rating'].name
        else:
            return ''

    def override_urls(self):
        # The detail URL for each resource must be listed before the list URL.
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/category"
                "/(?P<catpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_category_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/category%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_category_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/subcategory"
                "/(?P<subcatpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_subcategory_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/subcategory%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_subcategory_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/credit"
                "/(?P<credpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_credit_detail')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/credit%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_credit_list')),

            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/field"
                "/(?P<fieldpk>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_field_detail')),
                ]  # + self.base_urls()?

    def get_category_list(self, request, **kwargs):
        """Get a list of categories for the SubmissionSet with
        id = kwargs['pk']."""
        self.is_authenticated(request)
        try:
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        category_submission_resource = CategorySubmissionResource()
        return category_submission_resource.get_list(request,
                                                     submissionset=obj.pk)

    def get_category_detail(self, request, **kwargs):
        """Get the CategorySubmission that matches the Category
        where id = kwargs['catpk']."""
        self.is_authenticated(request)
        category_id = kwargs.pop('catpk')
        try:
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")
        return CategorySubmissionResource().get_detail(request,
                                                       submissionset_id=obj.pk,
                                                       category_id=category_id)

    def get_subcategory_list(self, request, **kwargs):
        """Get the list of SubcategorySubmissions for the SubmissionSet
        where id = kwargs['pk']."""
        self.is_authenticated(request)
        try:
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        return SubcategorySubmissionResource().get_list(
            request, submissionset_id=obj.pk)

    def get_subcategory_detail(self, request, **kwargs):
        """Get the SubcategorySubmission for the Subcategory where
        id = kwargs['subcatpk']."""
        self.is_authenticated(request)
        subcategory_id = kwargs.pop('subcatpk')
        # Make sure the submission set is valid:
        try:
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        kwargs['subcatpk'] = subcategory_id
        kwargs['submissionset'] = obj
        return SubcategorySubmissionResource().get_detail(
            request, **kwargs)

    def get_credit_list(self, request, **kwargs):
        """Get a list of credits for the SubmssionSet where
        id = kwargs['pk'].
        """
        self.is_authenticated(request)
        try:
            obj = self.cached_obj_get(request=request,
                                      **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        return CreditSubmissionResource().get_list(request,
                                                   submissionset_id=obj.pk)

    def get_credit_detail(self, request, **kwargs):
        """Get the CreditSubmissionResource that matches the Credit
        where id = kwargs['credpk'] and the SubmissionSet where
        id = kwargs['pk'].
        """
        self.is_authenticated(request)
        credit_id = kwargs.pop('credpk')
        try:
            submissionset = self.cached_obj_get(
                request=request,
                **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices(
                "More than one resource is found at this URI.")

        kwargs.pop('pk')
        kwargs['credpk'] = credit_id
        kwargs['submissionset'] = submissionset
        credit_submission_resource = CreditSubmissionResource()
        detail = credit_submission_resource.get_detail(request, **kwargs)
        return detail

    def get_field_detail(self, request, **kwargs):
        """Given the id's of a SubmissionSet (kwargs['pk']) and
        a DocumentationField (kwargs['fieldpk']), get the
        DocumentationFieldSubmissionResource that matches.
        """
        self.is_authenticated(request)
        for field_resource_type in (NumericSubmissionResource,
                                    TextSubmissionResource,
                                    NumericSubmissionResource,
                                    TextSubmissionResource,
                                    LongTextSubmissionResource,
                                    DateSubmissionResource,
                                    URLSubmissionResource,
                                    UploadSubmissionResource,
                                    BooleanSubmissionResource,
                                    ChoiceSubmissionResource,
                                    MultiChoiceSubmissionResource
                                    ):
            resources = field_resource_type().obj_get_list(
                request, submissionset_id=kwargs['pk'])
            try:
                resources.get(documentation_field__id=kwargs['fieldpk'])
                break
            except ObjectDoesNotExist:
                pass
        else:
            return HttpGone()

        kwargs['submissionset_id'] = kwargs.pop('pk')
        field_submission_resource = field_resource_type()
        detail = field_submission_resource.get_detail(request, **kwargs)
        return detail


class CategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any CategorySubmission
    """
    submissionset = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'SubmissionSetResource', 'submissionset')
    category = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'CategoryResource', 'category')
    subcategories = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'SubcategorySubmissionResource',
        'subcategorysubmission_set')

    class Meta(StarsApiResource.Meta):
        queryset = CategorySubmission.objects.all()
        resource_name = 'submissions/category'
        allowed_methods = ['get']
        filtering = { 'submissionset': 'exact',
                      'category': 'exact',
                      'id': ALL_WITH_RELATIONS }

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(CategorySubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        # default uri is
        #    submissions/category/<category-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/category/<category-id>
        # instead.
        submissionset_id = bundle_or_obj.obj.submissionset_id
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        category_id = str(bundle_or_obj.obj.category_id)
        return '/'.join(uri.split('/')[:-2] + [category_id, ''])

    def obj_get(self, request=None, **kwargs):
        """Given the id's for a SubmissionSet and a Category, get
        the matching CategorySubmission."""
        kwargs['submissionset'] = SubmissionSet.objects.get(
            pk=kwargs.pop('submissionset_id'))
        kwargs['category'] = Category.objects.get(pk=kwargs.pop('category_id'))
        return super(CategorySubmissionResource, self).obj_get(request,
                                                               **kwargs)


class SubcategorySubmissionResource(StarsApiResource):
    """
        Resource for accessing any SubcategorySubmission
    """
    subcategory = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'SubcategoryResource', 'subcategory')
    category = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'CategorySubmissionResource',
        'category_submission')
    submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'CreditSubmissionResource',
        'creditusersubmission_set')

    class Meta(StarsApiResource.Meta):
        queryset = SubcategorySubmission.objects.all()
        resource_name = 'submissions/subcategory'
        allowed_methods = ['get']
        filtering = { 'category': ALL_WITH_RELATIONS }

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(SubcategorySubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        # default uri is
        #    submissions/subcategory/<subcategory-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/subcategory/<subcategory-id>
        # instead.
        submissionset_id = \
          bundle_or_obj.obj.category_submission.submissionset_id
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        subcategory_id = str(bundle_or_obj.obj.subcategory_id)
        return '/'.join(uri.split('/')[:-2] + [subcategory_id, ''])

    def obj_get(self, request=None, **kwargs):
        """Given the id of a Subcategory and a SubmissionSet,
        get the matching SubcategorySubmission.
        """
        # TODO: BEN - does this SubcategorySubmission lookup look right?
        submissionset = kwargs.pop('submissionset')

        kwargs['pk'] = kwargs.pop('subcatpk')
        subcategory = Subcategory.objects.get(**kwargs)

        return subcategory.subcategorysubmission_set.get(
            category_submission__submissionset=submissionset)

    def obj_get_list(self, request=None, **kwargs):
        submissionset_id = kwargs.pop('submissionset_id')
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        return SubcategorySubmission.objects.filter(
            category_submission__in=categories_for_submissionset)


class CreditSubmissionResource(StarsApiResource):
    """
        Resource for accessing any CreditSubmission
    """
    credit = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'CreditResource', 'credit')
    subcategory = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'SubcategorySubmissionResource',
        'subcategory_submission')
    boolean_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'BooleanSubmissionResource',
        'booleansubmission_set')
    choice_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'ChoiceSubmissionResource',
        'choicesubmission_set')
    date_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'DateSubmissionResource',
        'datesubmission_set')
    longtext_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'LongTextSubmissionResource',
        'longtextsubmission_set')
    multichoicesubmission_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'MultiChoiceSubmissionResource',
        'multichoicesubmission_set')
    numeric_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'NumericSubmissionResource',
        'numericsubmission_set')
    text_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'TextSubmissionResource',
        'textsubmission_set')
    upload_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'UploadSubmissionResource',
        'uploadsubmission_set')
    url_submissions = fields.OneToManyField(
        SUBMISSIONS_RESOURCE_PATH + 'URLSubmissionResource',
        'urlsubmission_set')

    class Meta(StarsApiResource.Meta):
        queryset = CreditUserSubmission.objects.all()
        resource_name = 'submissions/credit'
        allowed_methods = ['get']
        # exclude submission_notes  becauses it raises
        # "'ascii' codec can't decode byte ... in position ...: ordinal not
        # in range(128)"
        excludes = ['submission_notes']

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        uri = super(CreditSubmissionResource, self).get_resource_uri(
            bundle_or_obj)
        # default uri is
        #    submissions/credit/<credit-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/credit/<credit-id>
        # instead.
        credit_user_submission = bundle_or_obj.obj.creditusersubmission
        subcategory_submission = credit_user_submission.subcategory_submission
        category_submission = subcategory_submission.category_submission
        submissionset_id = category_submission.submissionset.id
        uri = uri.replace('submissions/',
                          'submissions/{0}/'.format(submissionset_id))
        credit_id = str(bundle_or_obj.obj.credit_id)
        return '/'.join(uri.split('/')[:-2] + [credit_id, ''])

    def obj_get(self, request=None, **kwargs):
        """Given the id of a Credit and a SubmissionSet, get the matching
        CreditSubmission.
        """
        #TODO: BEN - what about this crazy get()?
        credit = Credit.objects.get(pk=kwargs['credpk'])
        return credit.creditsubmission_set.get(creditusersubmission__subcategory_submission__category_submission__submissionset=kwargs['submissionset']).creditusersubmission

    def obj_get_list(self, request=None, **kwargs):
        submissionset_id = kwargs.pop('submissionset_id')
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        subcategories_for_submissionset = \
          SubcategorySubmission.objects.filter(
              category_submission__in=categories_for_submissionset)
        return CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategories_for_submissionset)


class DocumentationFieldSubmissionResource(StarsApiResource):

    documentation_field = fields.ForeignKey(
        CREDITS_RESOURCE_PATH + 'DocumentationFieldResource',
        'documentation_field')
    credit_submission = fields.ForeignKey(
        SUBMISSIONS_RESOURCE_PATH + 'CreditSubmissionResource',
        'credit_submission')

    class Meta(StarsApiResource.Meta):
        resource_name = 'submissions/field'
        allowed_methods = ['get']

    def credit_user_submissions_for_submissionset(self,
                                                  submissionset_id):
        """Get all the CreditUserSubmission's for a
        SubmissionSet."""
        categories_for_submissionset = CategorySubmission.objects.filter(
            submissionset=submissionset_id)
        subcategories_for_submissionset = \
          SubcategorySubmission.objects.filter(
              category_submission__in=categories_for_submissionset)
        return(CreditUserSubmission.objects.filter(
            subcategory_submission__in=subcategories_for_submissionset))

    def get_resource_uri(self, bundle_or_obj=None,
                         url_name='api_dispatch_list'):
        # default uri is
        #    submissions/field/<field-submission-id>,
        # but we want to use
        #    submissions/<submission-set-id>/field/<field-id>
        # instead.
        # TODO: depending on the path on the incoming request is
        # bad, right?  If it's not, the all the other get_resource_uri
        # methods should do it this way, too:
        field_id = str(bundle_or_obj.obj.documentation_field_id)
        return '/'.join(bundle_or_obj.request.path.split('/')[:5] +
                        ['field', field_id, ''])

    def obj_get(self, request=None, **kwargs):
        """Given the id's of a SubmissionSet (kwargs['submissionset_id']) and
        and a DocumentationField (kwargs['fieldpk']), get the
        matching DocumentationFieldSubmission.
        """
        field_id = kwargs.pop('fieldpk')
        field_list = self.obj_get_list(request, **kwargs)
        field = field_list.get(documentation_field__id=field_id)
        return field

    def obj_get_list(self, request=None, **kwargs):
        """Get the DocumentationFieldSubmissionResource's *of this type*
        for the SubmissionSet where id = kwargs['submissionset_id'].

        This uses the queryset defined in subclass's Meta classes,
        so it's abstract.  So it doesn't get all the
        DocumentationFieldSubmission's for a SubmissionSet, only
        all instances of a particular subtype.
        """
        credit_user_submissions = \
          self.credit_user_submissions_for_submissionset(**kwargs)
        return self._meta.queryset.filter(
            credit_submission__in=credit_user_submissions)


class BooleanSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = BooleanSubmission.objects.all()


class ChoiceSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = ChoiceSubmission.objects.all()


class DateSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = DateSubmission.objects.all()


class LongTextSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = LongTextSubmission.objects.all()


class MultiChoiceSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = MultiChoiceSubmission.objects.all()


class NumericSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = NumericSubmission.objects.all()


class TextSubmissionResource(DocumentationFieldSubmissionResource):
    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = TextSubmission.objects.all()


class UploadSubmissionResource(DocumentationFieldSubmissionResource):
    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = UploadSubmission.objects.all()


class URLSubmissionResource(DocumentationFieldSubmissionResource):

    class Meta(DocumentationFieldSubmissionResource.Meta):
        queryset = URLSubmission.objects.all()
