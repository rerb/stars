from stars.apps.credits.models import *
from stars.apps.submissions.models import *

def migrate_set(old_cs, new_version_name, release_date):
    """ Copy a creditset to a new version and update `previous_version` references' """    
        
    def migrate_obj(old_obj, prop_dict, previous=True):
        
        new_obj = copy.copy(old_obj)
        new_obj.id = None
        if previous:
            new_obj.previous_version = old_obj
        for k,v in prop_dict.items():
            setattr(new_obj, k, v)
        new_obj.save()
        return new_obj
    
    new_cs = migrate_obj(old_cs, {'version': new_version_name, 'release_date': release_date})
    
    # ratings
    for r in old_cs.rating_set.all():
        new_r = migrate_obj(r, {'creditset': new_cs,})
        
    # categories, subcategories, credits, applicability reasons, documentation field, choice
    for cat in old_cs.category_set.all():
        new_cat = migrate_obj(cat, {'creditset': new_cs,})
        
        for sub in cat.subcategory_set.all():
            new_sub = migrate_obj(sub, {'category': new_cat,})
            
            for credit in sub.credit_set.all():
                new_c = migrate_obj(credit, {'subcategory': new_sub,})
                
                for ar in credit.applicabilityreason_set.all():
                    new_ar = migrate_obj(ar, {'credit': new_c,})
                    
                for field in credit.documentationfield_set.order_by('-id'):
                    new_f = migrate_obj(field, {'credit': new_c,})
                    
                    for choice in field.choice_set.all():
                        new_choice = migrate_obj(choice, {'documentation_field': new_f,})
                
                for cts in CreditTestSubmission.objects.filter(credit=credit):
                    new_cts = CreditTestSubmission(credit=new_c, expected_value=cts.expected_value)
                    new_cts.save()

                    for dfs in cts.get_submission_fields():
                        new_field = dfs.documentation_field.next_version
                        new_dfs = DocumentationFieldSubmission.get_field_class(dfs.documentation_field)(value=dfs.value, documentation_field=dfs.documentation_field.next_version, credit_submission=new_cts)
                        new_dfs.save()
    return new_cs