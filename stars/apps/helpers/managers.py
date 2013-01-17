from django.db import models

""" Generic, re-usable model managers """

class SelectRelatedManager(models.Manager):
    """ 
        This manager follows a set of foriegn keys to load related objects with single query
        To use it, add this line to your model:    
            objects = managers.SelectRelatedManager(('list','of','fields'))  # load applicability reason automatically
        To test it, try this code fragment with and without the manager enabled:
            >>> from django import db
            >>> db.reset_queries()
            >>> obj = Model.objects.get(pk=1)
            >>> len(db.connection.queries)
    """
    
    def __init__(self):
        """ 
            related_fields is a list of related fields to load automatically.  
            see: http://docs.djangoproject.com/en/dev/ref/models/querysets/#id4
        """
        super(SelectRelatedManager, self).__init__()
        self.related_fields = []
        
    def set_related_fields(self, related_field_list):
        self.related_fields = related_field_list
        
    def get_query_set(self):
        return super(SelectRelatedManager, self).get_query_set().select_related(*self.related_fields)

