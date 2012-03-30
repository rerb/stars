from django.db import models

class ThirdParty(models.Model):
    slug = models.SlugField(max_length=16)
    name = models.CharField(max_length=64)
    publication = models.CharField(max_length=128, blank=True, null=True)
    logo = models.ImageField(upload_to="tps", blank=True, null=True)
    next_deadline = models.DateField(blank=True, null=True)
    access_to_institutions = models.ManyToManyField("institutions.Institution", related_name='third_parties', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Third Parties"
        ordering = ['-next_deadline',]
    
    def __str__(self):
        return self.slug