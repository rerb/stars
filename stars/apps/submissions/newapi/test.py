import random
import urlparse

import stars.apps.api.test as stars_api
import stars.apps.submissions.models as submissions_models


class SubmissionsApiTest(stars_api.ApiTest):

    def __init__(self):
        super(SubmissionsApiTest, self).__init__(app_name='submissions')
        self.default_resource_name = 'submissionset'

    def runTest(self):
        models_map = {
            submissions_models.SubmissionSet: None,
            submissions_models.CategorySubmission: 'category',
            submissions_models.SubcategorySubmission: 'subcategory',
            submissions_models.CreditUserSubmission: 'credit',
            submissions_models.DocumentationFieldSubmission: 'field'
            }
        # models_map = {}
        super(SubmissionsApiTest, self).runTest(models_map=models_map,
                                                tearDown=False)

        # self.test_creditset_resource_link()

        # super(SubmissionsApiTest, self).tearDown()

    def test_creditset_resource_link(self):
        model_ids = [ instance.id for instance
                      in submissions_models.SubmissionSet.objects.all() ]
        lookup_id = model_ids[random.randint(0, len(model_ids) - 1)]
        json_response = eval(
            'self.registered_api.submissions.submissionset({0}).get()'.format(
                lookup_id))
        creditset_resource_uri = json_response['creditset'].strip('/')

        Reconstitute the link to the credit resource - take off parts
        common to self.registered_api._store['base_url'], then slap
        what's left on to ...['base_url]', then try to call via
        self.registered_api ...


        creditset_url_path = urlparse.urlsplit(creditset_resource_uri).path
        #
        lookup_id = creditset_resource_uri.split('/')[-1]
        eval_code = ('self.submissions.registered_api.' +
                     '.'.join(creditset_resource_uri.split('/')[:-1]) +
                     'get({0})'.format(lookup_id))
        eval(eval_code)

    def slumber_api_call(self, uri):
        def strip_split_slashes(s):
            return s.strip('/').split('/')
        parts = strip_split_slashes(uri)
        # if last element is int, put it in parens after prev element
        pk = parts.pop() if isinstance(parts[-1], int) else None
        leading_parts = strip_split_slashes(urlparse.urlparse(
            self.registered_api._store['base_url']).path)
        eval_source = '.'.join(leading_parts + parts)
        if pk:
            eval_source += '({pk})'.format(pk=pk)
        eval_source += '.get()'
        return eval(eval_source)

    def test_credits_resource_link(self, model, credit_resource_field_name,
                                   resource_name=None):
        """Test that the link to the credits resource that
        corresponds to this submission resource is there, and
        available.
        """
        model_ids = [ instance.id for instance in model.objects.all() ]
        lookup_id = model_ids[random.randint(0, len(model_ids) - 1)]
        resource_name = resource_name or model._meta.object_name.lower()
        json_response = eval(
            'self.registered_api.submissions.{0}({1}).get()'.format(
                resource_name, lookup_id))
        credit_resource_uri = json_response[credit_resource_field_name]
        eval_code = ('self.registered_api.submissions' +
                     credit_resource_uri.replace('/', '.') +
                     'get()')
        eval(eval_code)
