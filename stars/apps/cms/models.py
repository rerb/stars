import time
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

from stars.apps.cms import xml_rpc
from stars.apps.helpers import watchdog
from stars.apps.helpers.utils import invalidate_template_cache

class AbstractContent(models.Model):
    ordinal = models.SmallIntegerField(default=0)
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
class CategoryMixin(models.Model):
    content = models.TextField(blank=True, null=True)
    
    class Meta:
        abstract=True

    def get_articles(self):
        return self.newarticle_set.filter(published=True)

class Category(CategoryMixin, AbstractContent):
    """
        Django-hosted CMS top-level category
    """
    title = models.CharField(max_length=32)
    slug = models.SlugField()
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def get_absolute_url(self):
        return "/pages/%s/" % self.slug
    
class Subcategory(CategoryMixin, AbstractContent):
    
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
    
class NewArticle(AbstractContent):
    """
        Django-hosted CMS article
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField()
    teaser = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, null=True)
    subcategories = models.ManyToManyField(Subcategory, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    irc_id = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ('ordinal', 'title', 'timestamp',)
        verbose_name = "Article"
        verbose_name_plural = "Articles"
    
    def get_absolute_url(self):
        if self.subcategories.count() > 0:
            return "%s%s.html" % (self.subcategories.all()[0].get_absolute_url(), self.slug)
        elif self.categories.count() > 0:
            return "%s%s.html" % (self.categories.all()[0].get_absolute_url(), self.slug)
        return "#"
        
    def update_parent_timestamps(self):
        """
            Update the timestamps for caching purposes
            done in the admin
        """
        for sub in self.subcategories.all():
            sub.save()
            sub.parent.save()
        for cat in self.categories.all():
            cat.save()
            
def post_save_rec(sender, instance, **kwargs):
    instance.update_parent_timestamps()
post_save.connect(post_save_rec, sender=NewArticle)