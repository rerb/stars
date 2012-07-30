class DummyRequest(object):
    """ A dummy request object used for testing """
    def __init__(self, user):
        self.user = user
    def get_full_path(self):
        return "/dummy_path/"
