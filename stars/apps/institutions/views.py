
from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_is_staff
from stars.apps.institutions.models import Institution

# Currently, this is a staff-only tool, but it is designed to serve both staff and general public
# Once we have some registrants, remove this decorator and add the menu item (helpers.main_menu.py)
@user_is_staff
def institutions(request):
    """
        A list of institutions currently participating in STARS.
    """
    if request.user.is_staff:
        institutions = Institution.objects.filter()
    else:
        institutions = Institution.objects.filter(enabled=True)
        
    # Add the latest submission set and payment to each institution... but for staff only!
    for institution in institutions:
        institution.submission_set = None
        institution.payment = None
        if request.user.is_staff:
            submissions = institution.submissionset_set.order_by('-date_registered')
            if submissions:
                institution.submission_set = submissions[0]
                payments = institution.submission_set.payment_set.order_by('-date')
                if payments:
                    institution.payment = payments[0]
    template = "institutions/institution_list.html"
    return respond(request, template, {'institution_list':institutions})
