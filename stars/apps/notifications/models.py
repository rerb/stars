"""
    Templating tool to store email templates in the database
    and allow them to be edited and previewed
"""

from django.db import models
from django.utils.safestring import mark_safe

from utils import build_message

class EmailTemplate(models.Model):
    slug = models.SlugField(max_length=32, unique=True, help_text="Unique name. Please do not change.")
    title = models.CharField(max_length=128, help_text='The subjuect line of the email.')
    description = models.TextField()
    content = models.TextField()
    example_context = models.TextField(help_text="Example context for the template. Do not change.")
    
    class Meta:
        ordering = ('slug',)
        
    def get_message(self, content=None):
        """
            Renders the message with the supplied content.
            Uses self.content if no content is specified
        """
        if not content:
            content = self.content
        
        return build_message(content, eval(self.example_context))