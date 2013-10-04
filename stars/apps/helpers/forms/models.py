# File included for testing

from django.db import models

class TestModel(models.Model):
    f = models.BooleanField()
    t = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return "Imma Model"
