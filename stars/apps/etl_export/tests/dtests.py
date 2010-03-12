"""
    ETL Export Doctests
    
    Test Premises:
     - etl_export can create ETL entries
     - compare and replace changed entries
    
    >>> from stars.apps.institutions.models import Institution
    >>> from stars.apps.credits.models import CreditSet, Rating
    >>> from stars.apps.submissions.models import SubmissionSet
    >>> from stars.apps.etl_export.utils import *
    
    >>> from django.contrib.auth.models import User
    >>> from datetime import datetime, date
    
    >>> date1 = date(year=2010, month=1, day=1)
    >>> date2 = date(year=2010, month=2, day=2)
    
    >>> i = Institution(
    ...  aashe_id = -1,
    ...  name = "test institution",
    ...  contact_first_name = "first",
    ...  contact_last_name = "last",
    ...  contact_title = "title",
    ...  contact_department = "dept",
    ...  contact_phone = "800-555-1212",
    ...  contact_email = "test@example.com"
    ...  )
    >>> i.save()
    
    >>> cs = CreditSet(
    ...  version = 'test',
    ...  release_date = date1,
    ...  tier_2_points = 0.25,
    ...  is_locked = True,
    ...  scoring_method = 'get_STARS_v1_0_score',
    ... )
    >>> cs.save()
    
    >>> cs2 = CreditSet(
    ...  version = 'test2',
    ...  release_date = date1,
    ...  tier_2_points = 0.25,
    ...  is_locked = True,
    ...  scoring_method = 'get_STARS_v1_0_score',
    ... )
    >>> cs2.save()
    
    >>> r = Rating(
    ...  name = 'gold',
    ...  minimal_score = 0,
    ...  creditset = cs
    ... )
    >>> r.save()
    
    >>> u = User()
    >>> u.save()
    
    >>> ss = SubmissionSet(
    ...  institution = i,
    ...  creditset = cs,
    ...  date_registered = date1,
    ...  date_submitted = date1,
    ...  date_reviewed = date1,
    ...  submission_deadline = date1,
    ...  registering_user = u,
    ...  rating = r,
    ...  status = 'r',
    ... )
    >>> ss.save()
    
    >>> ss2 = SubmissionSet(
    ...  institution = i,
    ...  creditset = cs2,
    ...  date_registered = date2,
    ...  date_submitted = date2,
    ...  date_reviewed = date2,
    ...  submission_deadline = date2,
    ...  registering_user = u,
    ...  rating = None,
    ...  status = 'ps',
    ... )
    >>> ss2.save()
    
    >>> etl_a = populate_etl_entry(i)
    >>> etl_a.liaison_first_name
    'first'
    >>> etl_a.liaison_last_name
    'last'
    >>> etl_a.liaison_title
    'title'
    >>> etl_a.liaison_department
    'dept'
    >>> etl_a.liaison_phone
    '800-555-1212'
    >>> etl_a.liaison_email
    'test@example.com'
    >>> etl_a.latest_rating
    <Rating: gold>
    >>> etl_a.participant_status
    u'ps'
    
    >>> etl_b = populate_etl_entry(i)
    >>> etl_a == etl_b
    True
    >>> etl_a != etl_b
    False
    
    >>> ss2.status = 'pr'
    >>> ss2.save()
    >>> etl_c = populate_etl_entry(i)
    >>> print etl_c.participant_status
    pr
    >>> print etl_a.participant_status
    ps
    >>> etl_a == etl_c
    False
    
    >>> etl_1 = update_etl_for_institution(i, None)
    Added New ETL: -1
    
    >>> etl_2 = update_etl_for_institution(i, etl_1)
    No Change: -1
    
    >>> ss.status = 'pr'
    >>> ss.save()
    
    >>> etl_3 = update_etl_for_institution(i, etl_2)
    Updated ETL: -1
    
"""