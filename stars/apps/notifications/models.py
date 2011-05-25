"""
    Templating tool to store email templates in the database
    and allow them to be edited and previewed
"""

from django.db import models
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage

from jsonfield import JSONField

from utils import build_message

class EmailTemplate(models.Model):
    slug = models.SlugField(max_length=32, unique=True, help_text="Unique name. Please do not change.")
    title = models.CharField(max_length=128, help_text='The subjuect line of the email.')
    description = models.TextField()
    content = models.TextField()
    example_data = JSONField(help_text="Example context for the template. Do not change.")
    
    class Meta:
        ordering = ('slug',)
        
    def get_message(self, content=None, context=None):
        """
            Renders the message with the supplied content.
            Uses self.content if no content is specified
            Uses self.example_data if not context is specified
        """
        if not content:
            content = self.content
            
        if not context:
            context = self.example_data
        
        return build_message(content, context)
        
    def send_email(self, mail_to, context):
    
        m = EmailMessage(
                        subject=self.title,
                        body=build_message(self.content, context),
                        to=mail_to,
                        bcc=['ben@aashe.org',],
                        headers = {'Reply-To': 'stars@aashe.org'},
                    )
        m.send()
        
    def get_absolute_url(self):
        return "/notifications/preview/%s/" % self.slug