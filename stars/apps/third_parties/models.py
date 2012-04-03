from django.db import models

from stars.apps.submissions.models import SubmissionSet

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
    
    def get_snapshots(self):
        """
            Get all the available snapshots for this third party
        """
        qs = SubmissionSet.objects.filter(status='f').filter(institution__in=self.access_to_institutions.all())
        return qs
    
    def get_snapshot_institution_count(self):
        """
            Get just the number of institutions that have shared snapshots
        """
        count = 0
        for i in self.access_to_institutions.all():
            if i.submissionset_set.filter(status='f').count() > 0:
                count += 1
        return count
            