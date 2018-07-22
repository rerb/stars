# Common methods for BT ETL

from stars.apps.credits.models import DocumentationField
from stars.apps.submissions.models import DocumentationFieldSubmission


def get_datapoint_key(obj):
    """
    Get's a key for each datapoint
    """
    if obj.__class__.__name__ == "CreditSet":
        return 'overall'
    lookups = {
        'Category': 'cat',
        'Subcategory': 'sub',
        'Credit': 'cred',
        'DocumentationField': 'field'
    }
    return "%s_%d" % (lookups[obj.__class__.__name__], obj.id)


def get_latest_df_val_for_institution(df_id, institution):
    
    df = DocumentationField.objects.get(pk=df_id)
    # start at the most recent submission
    for ss in institution.submissionset_set.filter(status='r').order_by('-date_submitted'):
        # get the field for this creditset
        rel_df = df.get_for_creditset(ss.creditset)
        Klass = DocumentationFieldSubmission.get_field_class(df)
        dfs = Klass.objects.by_submissionset(ss)
        dfs = dfs.get(documentation_field=rel_df)
        if dfs.value:
            if Klass.__name__ == 'ChoiceSubmission':
                return dfs.value.choice
            else:
                return dfs.value
    return None
    

def get_institution_type(institution):
    """
        tries to get the institution type from submissions
        starting with the latest
    """
    _type = get_latest_df_val_for_institution(4368, institution)
    
    # print _type
    if _type:
        return _type
        
    assert False
    return None

def get_institution_control(institution):
    
    _control = get_latest_df_val_for_institution(4367, institution)
    
    # print _control
    if _control:
        return _control
        
    assert False
    return None

def get_institution_fte_cat(institution):
    """
        Less than 5,000
        5,000-9,999
        10,000-19,999
        20,000+
    """
    
    ranges = (
        {'range': [0, 4999], 'label': "Less than 5,000"},
        {'range': [5000, 9999], 'label': "5,000-9,999"},
        {'range': [10000, 19999], 'label': "10,000-19,999"},
        {'range': [20000, 10000000], 'label': "20,000+"},
    )
    
    _fte = get_latest_df_val_for_institution(4409, institution)
    # print _fte
    
    if _fte:
        for r in ranges:
            if _fte > r['range'][0] and _fte <= r['range'][1]:
                return r['label']
    
    assert False
    return None