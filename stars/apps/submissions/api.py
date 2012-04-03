from models import SubmissionSet
from tastypie import fields
from tastypie.resources import ModelResource, Resource
from tastypie.bundle import Bundle
from tastypie.cache import SimpleCache

from django.core.urlresolvers import reverse
from django.core.cache import cache

from stars.apps.submissions.models import SubmissionSet, SubcategorySubmission, CreditUserSubmission
from stars.apps.credits.models import Category, Subcategory

import sys

class Chart(object):
    """
        A pie chart representation
    """
    def __init__(self, name, id, slices):
        self.name = name
        self.id = id
        self.slices = slices
        
#    def __str__(self):
#        return self.name
        
class Slice(object):
    """
        A representation of a pie chart slice
    """
    def __init__(self, title, long_title, id, value, fill_fraction, child_chart=None):
        self.title = title
        self.long_title = long_title
        self.id = id
        self.value = value
        self.fill_fraction = fill_fraction
        self.child_chart = child_chart

class GetCacheMixin(object):
    
    def get_cache_key(self, request):
        raise NotImplementedError
    
    def obj_get(self, request = None, **kwargs):
        """
            wrapper that caches the result of this method
        """

        
        object = super(CacheMixin, self).obj_get(request, kwargs)
        
        cache.set(key, object, 60*60*5)
        
        return object
    
    def obj_get_list(self, request=None, **kwargs):
        """
            wrapper that caches the result of this method
        """
        key = self.get_cache_key(request)
        obj_list = cache.get(key)
        if obj_list:
            print "CACHE HIT: %s" % key
            return obj_list
        print >> sys.stderr, "CACHE MISS: %s" % key
        
        obj_list = super(CacheMixin, self).obj_get(request, kwargs)
        
        cache.set(key, obj_list, 60*60*5)
        
        return obj_list

class SliceMixin(object):
    
    def dehydrate_slices(self, bundle):
        slices = []
        for obj in bundle.obj.slices:
            slices.append({
                            'title': obj.title,
                            'long_title': obj.long_title,
                            'id': obj.id,
                            'value': obj.value,
                            'fill_fraction': obj.fill_fraction,
                            'child_chart': obj.child_chart
                            })
        return slices
        
#    def __str__(self):
#        return self.title

class SummaryPieChart(Resource, SliceMixin):
    name = fields.CharField(attribute = 'name')
    id = fields.IntegerField(attribute = 'id')
    slices = fields.ListField(attribute = 'slices')
    
    class Meta:
        resource_name = "summary-pie-chart"
        object_class = Chart
        allowed_methods = ['get']
    
    def obj_get_list(self, request=None, **kwargs):
        """
            For each category:
                average score
                available points
                
            {
                'OP': { 'running_total': 0, 'running_count': 0, 'title': title, 'id': id, 'max': max_point_value }
            }
        """
        
        key = self.generate_cache_key('detail', **kwargs)
        object = cache.get(key)
        if object:
            return object
        
        scores = {}
        
        for ss in SubmissionSet.objects.get_rated():
            if ss.rating.publish_score:
                for cat in ss.categorysubmission_set.order_by('category__ordinal').filter(category__include_in_score=True):
                    # @todo: exclude supplemental
                    latest = cat.category.get_latest_version()
                    if scores.has_key(cat.category.abbreviation):
                        scores[latest.abbreviation]['running_total'] += cat.score
                        scores[latest.abbreviation]['running_count'] += 1
                    else:
                        scores[latest.abbreviation] = {
                                                                'running_count': 1,
                                                                'running_total': cat.score,
                                                                'title': latest.title,
                                                                'long_title': latest.title,
                                                                'id': cat.category.get_latest_version().id
                                                            }
                        if cat.category.abbreviation != "IN":
                            scores[cat.category.abbreviation]['value'] = 32
                            scores[cat.category.abbreviation]['max'] = 100
                        else:
                            scores[cat.category.abbreviation]['value'] = 4
                            scores[cat.category.abbreviation]['max'] = 4
        
        slices = []
        for k, v in scores.items():
            slices.append(
                            Slice(
                                    title=v['title'],
                                    long_title=v['long_title'],
                                    id="cat_%d" % v['id'],
                                    value=v['value'],
                                    fill_fraction=(v['running_total'] / v['running_count']) / v['max'],
                                    child_chart="/api/v1/category-pie-chart/%d/" % v['id']
                          ))
        
        c = Chart("top_level_chart", "1", slices)
        cache.set(key, [c,], 60*60*24)
        return [c,]

class CategoryPieChart(Resource, SliceMixin):
    name = fields.CharField(attribute = 'name')
    id = fields.IntegerField(attribute = 'id')
    slices = fields.ListField(attribute = 'slices')
    
    class Meta:
        resource_name = "category-pie-chart"
        object_class = Chart
        allowed_methods = ['get']
    
    # https://gist.github.com/794424
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id # pk is referenced in ModelResource
        else:
            kwargs['pk'] = bundle_or_obj.id
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)
    
    def obj_get(self, request = None, **kwargs):
        """
            Get one chart object for the specific category
            
            using a 1.1 category, should have the same result as a 1.2 category
            because I use the abbreviation instead of the id
        """
        key = self.generate_cache_key('detail', **kwargs)
        object = cache.get(key)
        if object:
            return object
        
        pk = int(kwargs['pk'])
        try:
            obj = self.build_chart_from_category(Category.objects.get(pk=pk))
            cache.set(key, obj, 60*60*24)
            return obj
        except Category.DoesNotExist:
            raise NotFound("Object not found")
    
    def obj_get_list(self, request=None, **kwargs):
        """
            Get a list of charts for each category
            
            Note: we're using the abbreviation to be sure we get all the categories
            @todo - it might be worth using the VersionedModel methods eventually
            because abbreviations might change
        """
        
        obj_list = []
        
        abbreviation_list = []
        for category in Category.objects.filter(include_in_score=True):
            if category.abbreviation not in abbreviation_list:
                abbreviation_list.append(category.abbreviation)
                obj_list.append(self.build_chart_from_category(category))
                
        return obj_list

    def build_chart_from_category(self, category):
        
        qs = SubcategorySubmission.objects.filter(category_submission__category__abbreviation=category.abbreviation)
        qs = qs.filter(category_submission__submissionset__status='r')
        qs = qs.filter(category_submission__submissionset__is_locked=False)
        qs = qs.filter(category_submission__submissionset__is_visible=True)
        
        slice_dict = {}
        
        for sub in qs:
            if sub.category_submission.submissionset.rating.publish_score:
                latest = sub.subcategory.get_latest_version()
                if slice_dict.has_key(latest.id):
                    slice_dict[latest.id]['running_total'] += sub.get_claimed_points()
                    slice_dict[latest.id]['running_count'] += 1
                else:
                    slice_dict[latest.id] = {
                                                "running_total": sub.get_claimed_points(),
                                                "running_count": 1,
                                                "title": latest.title,
                                                "long_title": latest.title,
                                                "id": latest.id,
                                                "max": sub.get_available_points(),
                                              }
        slices = []
        for k, v in slice_dict.items():
            slices.append(
                            Slice(
                                    title=v['title'],
                                    long_title=v['long_title'],
                                    id="sub_%d" % v['id'],
                                    value=v['max'],
                                    fill_fraction=(v['running_total'] / v['running_count']) / v['max'],
                                    child_chart="/api/v1/subcategory-pie-chart/%d/" % v['id']
                          ))
        
        c = Chart(category.title, category.id, sorted(slices, key=lambda slice:slice.title))
        return c

class SubategoryPieChart(Resource, SliceMixin):
    name = fields.CharField(attribute = 'name')
    id = fields.IntegerField(attribute = 'id')
    slices = fields.ListField(attribute = 'slices', null=True)
    
    class Meta:
        resource_name = "subcategory-pie-chart"
        object_class = Chart
        allowed_methods = ['get']
        
#    def generate_cache_key(self, title, **kwargs):
#        key = "%s_%s" % (title, self._meta.resource_name)
#        if kwargs.has_key('pk'):
#            return "%s_%s" % (key, kwargs['pk'])
#        return key
    
    # https://gist.github.com/794424
    def get_resource_uri(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id # pk is referenced in ModelResource
        else:
            kwargs['pk'] = bundle_or_obj.id
        
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name
        
        return self._build_reverse_url('api_dispatch_detail', kwargs = kwargs)
    
    def obj_get(self, request=None, **kwargs):
        """
            Get one chart object for the specific category
            
            using a 1.1 category, should have the same result as a 1.2 category
            because I use the abbreviation instead of the id
        """
        key = self.generate_cache_key('detail', **kwargs)
        object = cache.get(key)
        if object:
            return object
        
        pk = int(kwargs['pk'])
        try:
            obj = self.build_chart_from_subcategory(Subcategory.objects.get(pk=pk))
            cache.set(key, obj, 60*60*24)
            return obj
        except Category.DoesNotExist:
            raise NotFound("Object not found")
    
    def obj_get_list(self, request=None, **kwargs):
        """
            Get a list of charts for each subcategory
            
            Note: we're using the abbreviation to be sure we get all the categories
            @todo - it might be worth using the VersionedModel methods eventually
            because abbreviations might change
        """
        
        obj_list = []
        
        title_list = []
        for sub in Subcategory.objects.filter(category__include_in_score=True):
            if sub.title not in title_list:
                title_list.append(sub.title)
                obj_list.append(self.build_chart_from_subcategory(sub))
                
        return obj_list

    def build_chart_from_subcategory(self, subcategory):
        """
            Generate a slice for each credit in the subcategory
        """
        
        sub_list = subcategory.get_all_versions()
        
        qs = CreditUserSubmission.objects.filter(subcategory_submission__subcategory__in=sub_list)
        qs = qs.filter(subcategory_submission__category_submission__submissionset__status='r')
        qs = qs.filter(subcategory_submission__category_submission__submissionset__is_locked=False)
        qs = qs.filter(subcategory_submission__category_submission__submissionset__is_visible=True)
        qs = qs.filter(subcategory_submission__category_submission__category__include_in_score=True)
        
        slice_dict = {}
        
        total = qs.count()
        count = 0
        
        for c in qs:
            count += 1
            latest = c.credit.get_latest_version()
            key = latest.get_identifier()
            if slice_dict.has_key(key):
                slice_dict[key]['running_total'] += c.assessed_points
                slice_dict[key]['running_count'] += 1
            else:
                slice_dict[key] = {
                                    "running_total": c.assessed_points,
                                    "running_count": 1,
                                    "title": key,
                                    "long_title": "%s: %s" % (key, latest.title),
                                    "id": latest.id,
                                    "max": latest.point_value,
                                    }
        slices = []
        for k, v in slice_dict.items():
            slices.append(
                            Slice(
                                    title=v['title'],
                                    long_title=v['long_title'],
                                    id="credit_%d" % v['id'],
                                    value=v['max'],
                                    fill_fraction=(v['running_total'] / v['running_count']) / v['max']
                          ))
        
        c = Chart(subcategory.title, subcategory.id, sorted(slices, key=lambda slice:slice.title))
        
        return c

class SubmissionSetResource(ModelResource):
    class Meta:
        queryset = SubmissionSet.objects.all()
        fields = ['creditset', 'institution', 'score']
        resource_name = "viz"
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        # add all the categories and credits
        
        categories = []
        for cat in bundle.obj.categorysubmission_set.all():
            credits = []
            if cat.category.abbreviation == "IN":
                available_points = 4
            else:
                available_points = 100
            cat_dict = {
                            "id": cat.id,
                            "abbreviation": cat.category.abbreviation,
                            "title": cat.category.title,
                            "available_points": available_points,
                            "assessed_points": round(cat.get_STARS_score(), 2),
            }
            for sub in cat.subcategorysubmission_set.all():
                for cus in sub.creditusersubmission_set.all():
                    credits.append(
                                    {
                                        "id": cus.id,
                                        "assessed_points": round(cus.assessed_points, 2),
                                        "available_points": cus.credit.point_value,
                                        "identifier": cus.credit.get_identifier(),
                                        "title": cus.credit.title,
                                    }
                    )
            cat_dict['credits'] = credits
            categories.append(cat_dict)
        bundle.data['categories'] = categories
    
        return bundle