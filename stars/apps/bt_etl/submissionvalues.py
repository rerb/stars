from datetime import datetime
import io
import json

from stars.apps.submissions.models import SubmissionSet, NumericSubmission
from django.db.models import Q
from stars.apps.bt_etl.utils import get_datapoint_key


def extract_and_transform(filename='submissionvalue.json'):

    MODEL_STRING = "stars_content.submissionvalue"
    STARS_URL = "https://stars.aashe.org"
    
    """
    [
    {
      "model": "stars_content.submissionvalue",
      "pk": 1,
      "fields": {
        data_point_key = models.CharField(max_length=16)
        title = models.CharField(max_length=128)
        short_title = models.CharField(max_length=64)
        is_numeric = models.BooleanField(default=True)
        imperial_value = models.FloatField(blank=True, null=True)
        imperial_units = models.CharField(max_length=16, blank=True, null=True)
        metric_value = models.FloatField(blank=True, null=True)
        metric_units = models.CharField(max_length=16, blank=True, null=True)
        text_value = models.TextField(blank=True, null=True)
        display_value = models.TextField(blank=True, null=True)
        detail_url = models.URLField()
    
        # Report information
        report_id = models.IntegerField()
        overall_score = models.FloatField()
        rating_name = models.CharField(max_length=16)
        rating_ordinal = models.IntegerField()
        is_latest = models.BooleanField()
        is_expired = models.BooleanField()
        report_url = models.URLField()
    
        # Institution Data
        inst_id = models.IntegerField()
        inst_name = models.CharField(max_length=255)
        inst_aashe_id = models.IntegerField(unique=True, blank=True, null=True)
        inst_fte = models.IntegerField(blank=True, null=True)
        inst_is_pcc_signatory = models.NullBooleanField(default=False)
        inst_is_member = models.NullBooleanField(default=False)
        inst_country = models.CharField(max_length=128, blank=True, null=True)
        inst_type = models.CharField(
            max_length=128, blank=True, null=True)
        inst_rating_name = models.CharField(max_length=16, blank=True, null=True)
        inst_rating_ordinal = models.IntegerField()
      }
    },
    ...]
    """
    
    
    def get_base_subdata(obj, ss):
        
        i = ss.institution
        
        obj = {
            'model': MODEL_STRING,
            'pk': None, # needs to be set by django
            'fields': {
                
                # Submission Properties
                'report_id': ss.id,
                'report_version': ss.creditset.version,
                'overall_score': ss.score,
                'rating_name': ss.rating.name,
                'rating_ordinal': ss.rating.minimal_score,
                'is_current': ss.id == ss.institution.rated_submission.id,
                'is_latest': (
                    ss.id == ss.institution.rated_submission.id or
                    (
                        ss.institution.latest_expired_submission != None and
                        ss.id == ss.institution.latest_expired_submission.id
                    )
                ),
                'is_expired': ss.expired,
                'report_url': "%s%s" % (STARS_URL, ss.get_scorecard_url()),
                
                # Institution Properties
                'inst_id': i.id,
                'inst_name': i.name,
                'inst_aashe_id': i.aashe_id,
                'inst_fte': i.fte,
                'inst_is_pcc_signatory': i.is_pcc_signatory,
                'inst_is_member': i.is_member,
                'inst_country': i.country,
                'inst_type': i.institution_type,
                'inst_rating_name': None,
                'inst_rating_ordinal': None
            }
        }
    
        if i.current_rating:
            obj['fields']['inst_rating_name'] = i.current_rating.name
            obj['fields']['inst_rating_ordinal'] = i.current_rating.minimal_score
        
        return obj
        
    def update_score_fields(etl_obj, obj, parent, title, short_title, value, url, imperial_units, metric_units, display_value=None):
        
        etl_obj['fields']['data_point_key'] = get_datapoint_key(parent)
        etl_obj['fields']['title'] = title
        etl_obj['fields']['short_title'] = short_title
        etl_obj['fields']['is_numeric'] = True
        etl_obj['fields']['imperial_value'] = value
        etl_obj['fields']['imperial_units'] = imperial_units
        etl_obj['fields']['metric_value'] = value # @todo - FIX!! - also... set to imperial value when no units or %
        etl_obj['fields']['metric_units'] = metric_units
        etl_obj['fields']['text_value'] = None
        etl_obj['fields']['detail_url'] = "%s%s" % (STARS_URL, url)
        etl_obj['fields']['display_value'] = display_value
    
        return etl_obj
    
    
    def get_ss_obj(ss):
        
        obj_list = []
        
        # Add overall, category, subcategory, and credit scores
        
        etl_obj = get_base_subdata(ss, ss)
        update_score_fields(
            etl_obj,
            ss,
            ss.creditset,
            "Overall Score",
            "Overall Score",
            ss.score,
            ss.get_scorecard_url(),
            "%", "%")
        obj_list.append(etl_obj)
        
        for cat in ss.categorysubmission_set.all():
            etl_obj = get_base_subdata(cat, ss)
            r = cat.get_score_ratio()
            score = 0
            if r[1] > 0 and r[0]:
                score = (r[0] / r[1]) * 100
            update_score_fields(
                etl_obj,
                cat,
                cat.category,
                "%s Score" % cat.category.title,
                cat.category.title,
                score,
                ss.get_scorecard_url(),
                "%", "%"
            )
            obj_list.append(etl_obj)
            
            for sub in cat.subcategorysubmission_set.all():
                etl_obj = get_base_subdata(sub, ss)
                score = sub.percentage_score * 100 if sub.percentage_score else 0
                update_score_fields(
                    etl_obj,
                    sub,
                    sub.subcategory,
                    "%s Score" % sub.subcategory.title,
                    sub.subcategory.title,
                    score,
                    ss.get_scorecard_url(),
                    "%", "%"
                )
                obj_list.append(etl_obj)
                
                for credit in sub.creditusersubmission_set.all():
                    etl_obj = get_base_subdata(credit, ss)
                    dv = None
                    if credit.is_na():
                        dv = "Not Applicable"
                    if not credit.is_pursued():
                        dv = "Not Pursued"
                    
                    score = 0
                    if credit.assessed_points > 0 and credit.get_available_points(use_cache=True) > 0:
                        score = credit.assessed_points / credit.get_available_points(use_cache=True) * 100
                    
                    update_score_fields(
                        etl_obj,
                        credit,
                        credit.credit,
                        "%s Score" % credit.credit.title,
                        credit.credit.title,
                        score,
                        credit.get_scorecard_url(),
                        "%", "%",
                        display_value=dv
                    )
                    obj_list.append(etl_obj)
                    
                    for field in credit.numericsubmission_set.filter(value__isnull=False):
                        etl_obj = get_base_subdata(field, ss)
                        df = field.documentation_field
                        
                        imperial_units = df.us_units.name if df.us_units else None
                        metric_units = df.metric_units.name if df.metric_units else None
                        if not imperial_units:
                            if 'percentage' in df.title or "Percentage" in df.title:
                                metric_units = "%"
                                imperial_units = "%"
            
                        update_score_fields(
                            etl_obj,
                            field,
                            df,
                            df.title,
                            df.title,
                            field.value if dv == None else None,
                            credit.get_scorecard_url(),
                            imperial_units,
                            metric_units,
                            display_value=dv
                        )
                        etl_obj['fields']['imperial_value'] = field.value
                        etl_obj['fields']['metric_value'] = field.metric_value
                        obj_list.append(etl_obj)
                    
                    
        return obj_list;
        
    
    with io.open(filename, 'w', encoding='utf-8') as f:
        
        f.write(u"[")
        qs = SubmissionSet.objects.filter(status='r')
        qs = qs.filter(creditset__version="2.1")[:4]
        total = qs.count()
        count = 0
        for ss in qs:
            count += 1
            print "%s of %s" % (count, total)
            obj_list = get_ss_obj(ss)
        
            inner_count = 0
            for o in obj_list:
                inner_count += 1
                r_json = json.dumps(o, ensure_ascii=False, indent=2)
                f.write(r_json)
                if (count != total or inner_count != len(obj_list)):
                    f.write(u",")
        f.write(u"]")
