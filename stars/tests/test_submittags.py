from apps.tool.my_submission.templatetags.submit_tags import format_available_points

from apps.submissions.models import *
"""
    Tests for the submission tags
    
    usage: python manage.py execfile tests/test_submittags.py
    
    THIS HAS BEEN CONVERTED INTO A Submissions UNIT TEST
"""

ss = SubcategorySubmission.objects.all()[0]

print format_available_points(ss)
