from django.db import models

class HelpContext(models.Model):
    """
        Help text context tool to store commonly used help contexts.
    """
    name = models.CharField(max_length=32)
    help_text = models.TextField()
    
    def __unicode__(self):
        return self.name
        
class BlockContent(models.Model):
    """
        A tool to house content that can be edited on the site.
    """
    key = models.CharField(max_length=16, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.key