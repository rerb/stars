import stars.apps.api.test as stars_api
import stars.apps.credits.models as credits_models


class CreditsApiTest(stars_api.ApiTest):

    def __init__(self):
        super(CreditsApiTest, self).__init__(app_name='credits')
        self.default_resource_name = 'creditset'

    def runTest(self):
        models_map = {
            credits_models.CreditSet: None,
            credits_models.Category: None,
            credits_models.Subcategory: None,
            credits_models.Credit: None,
            credits_models.DocumentationField: 'field' }
        super(CreditsApiTest, self).runTest(models_map=models_map)
