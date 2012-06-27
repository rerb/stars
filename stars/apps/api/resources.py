from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

TESTING = False  # When TESTING is True, authentication is turned off.


class JSONForHTMLSerializer(Serializer):
    """
        Serializer that returns JSON when asked for HTML.  Removes
        requirement for requests from web browsers to specify a
        format.
    """
    def to_html(self, data, options):
        return self.to_json(data, options)


class StarsApiResource(ModelResource):
    """
        Base class for STARS API resources.
    """
    class Meta:
        if TESTING:
            authentication = Authentication()
            print 'WARNING: no authentication active'
        else:
            authentication = ApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        serializer = JSONForHTMLSerializer()
