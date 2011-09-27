from django.db import models
from django.core import urlresolvers

class HelpContext(models.Model):
    """
        Help text context tool to store commonly used help contexts.
    """
    name = models.CharField(max_length=32)
    help_text = models.TextField()
    
    def __unicode__(self):
        return self.name
    
    def get_admin_url(self):
        return urlresolvers.reverse('admin:helpers_helpcontext_change', args=(self.id,))
        
class BlockContent(models.Model):
    """
        A tool to house content that can be edited on the site.
    """
    key = models.SlugField(unique=True)
    content = models.TextField()

    def __str__(self):
        return self.key
    
    def get_admin_url(self):
        return urlresolvers.reverse('admin:helpers_blockcontent_change', args=(self.id,))
