import time
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from stars.apps.cms import xml_rpc
from stars.apps.helpers import watchdog
from stars.apps.helpers.utils import invalidate_template_cache

class AbstractContent(models.Model):
    ordinal = models.SmallIntegerField(default=0)
    content = models.TextField()
    published = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ('ordinal','title')
        
    def __str__(self):
        return self.title
    
    def get_django_admin_url(self):
        return "/_ad/%s/%s/%d" % (
                                    self._meta.app_label,
                                    self._meta.module_name,
                                    self.id,
                                )
        
    def get_articles(self):
        return self.article_set.filter(published=True)

class Category(AbstractContent):
    """
        Django-hosted CMS top-level category
    """
    title = models.CharField(max_length=32)
    slug = models.SlugField()
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def get_absolute_url(self):
        return "/pages/%s/" % self.slug
    
class Subcategory(AbstractContent):
    
    title = models.CharField(max_length=32)
    slug = models.SlugField()
    parent = models.ForeignKey(Category)
    
    class Meta:
        verbose_name_plural = "Subcategories"
    
    def get_absolute_url(self):
        return "%s%s/" % (self.parent.get_absolute_url(), self.slug)
    
    def save(self, *args, **kwargs):
        super(Subcategory, self).save(*args, **kwargs)
        self.parent.save() # Update timestamp for caching
    
class Article(AbstractContent):
    """
        Django-hosted CMS article
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    teaser = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    subcategories = models.ManyToManyField(Subcategory, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    irc_id = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ('ordinal', 'title', 'timestamp',)
    
    def get_absolute_url(self):
        if self.subcategories.count() > 0:
            return "%s%s.html" % (self.subcategories.all()[0].get_absolute_url(), self.slug)
        elif self.categories.count() > 0:
            return "%s%s.html" % (self.categories.all()[0].get_absolute_url(), self.slug)
        return "#"
    
    def save(self, *args, **kwargs):
        """
            Update the timestamps for caching purposes
        """
        for sub in self.subcategories.all():
            sub.save()
        for cat in self.categories.all():
            cat.save()
        super(Article, self).save(*args, **kwargs)