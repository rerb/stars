from django.db import models

class HelpContext(models.Model):
    """
        Help text context tool to store commonly used help contexts.
    """
    name = models.CharField(max_length='32')
    help_text = models.TextField()
    
    def __unicode__(self):
        return self.name