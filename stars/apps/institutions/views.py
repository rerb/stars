from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_is_staff, user_can_view
from stars.apps.credits.models import CreditSet
from stars.apps.submissions.models import *
from stars.apps.institutions.models import Institution, InstitutionState

# Currently, this is a staff-only tool, but it is designed to serve the general public
# All staff-only features have been moved to the admin institutions_list view/template.
# Once we have some registrants, remove this decorator and add the menu item (helpers.main_menu.py)
@user_is_staff
def institutions_rated(request):
    """
        A list of institutions with at least one STARS rating (complete credit set).
    """
    # @todo: need to add a State field to store latest rated submission set - use that here.
    # Loading State objects here so both institutions and their queryset are loaded in one query
    # Can change this to load Institutions once this ticket is resolved: http://code.djangoproject.com/ticket/7270
    institutions = InstitutionState.objects.select_related('institution', 'latest_rated_submission_set')\
                                           .filter(institution__enabled=True)\
                                           .filter(latest_rated_submission_set__status='r')
    
    columns = [{'sort_key':'name','sort_field':'institution__name', 'label':'Institution', 'img':None},
               {'sort_key':'rating','sort_field':'latest_rated_submission_set__rating', 'label':'STARS Rating', 'img':None},
               {'sort_key':'version','sort_field':'latest_rated_submission_set__creditset__version', 'label':'STARS Version', 'img':None},
               {'sort_key':'date_reviewed','sort_field':'latest_rated_submission_set__date_reviewed', 'label':'Date Approved', 'img':None},
# @todo: we're not storing the score yet - perhaps we should do this upon rating?
               {'sort_key':'score', 'sort_field':'id', 'label':'Overall Score', 'img':None},
              ]
    institutions, sort_columns = _get_sort_order(columns, request.GET.get('sort', None), institutions)

    template = "institutions/institution_list_rated.html"
    return respond(request, template, {'institution_list':institutions, 
                                       'sort_columns':sort_columns,
                                       'creditset':CreditSet.get_latest_creditset()})

# Currently, this is a staff-only tool, but it is designed to serve the general public
@user_is_staff
def institutions_active(request):
    """
        A list of institutions currently participating in STARS (with an active, unrated submissionset)
    """
    # Can change this to load Institutions once this ticket is resolved: http://code.djangoproject.com/ticket/7270
    institutions = InstitutionState.objects.select_related('institution', 'active_submission_set')\
                                           .filter(institution__enabled=True)\
                                           .exclude(active_submission_set__status='r')
    
    columns = [{'sort_key':'name', 'sort_field':'institution__name', 'label':'Institution', 'img':None},
               {'sort_key':'version', 'sort_field':'active_submission_set__creditset__version', 'label':'STARS Version', 'img':None},
               {'sort_key':'date_registered', 'sort_field':'active_submission_set__date_registered', 'label':'Date Registered', 'img':None},
               {'sort_key':'submission_deadline', 'sort_field':'active_submission_set__submission_deadline', 'label':'Submission Deadline', 'img':None},
# @todo: we're not storing the progress - hmmmm
               {'sort_key':'progress', 'sort_field':'id', 'label':'Progress', 'img':None},
              ]
    institutions, sort_columns = _get_sort_order(columns, request.GET.get('sort', None), institutions)
                        
    template = "institutions/institution_list_active.html"
    return respond(request, template, {'institution_list':institutions, 
                                       'sort_columns':sort_columns,
                                       'creditset':CreditSet.get_latest_creditset()})

def _get_sort_order(columns, sort_order, institutions):

    if sort_order:
        if sort_order[0]=='-':
            sort_key = sort_order[1:]
            sort_desc = '-'
            sort_reverse = ''
            img = 'sort_desc.png'
        else:
            sort_key = sort_order
            sort_desc = ''
            sort_reverse = '-'
            img = 'sort_asc.png'

        for col in columns:
            if col['sort_key'] == sort_key:
                institutions = institutions.order_by("%s%s"%(sort_desc, col['sort_field']))
                col['sort_key'] = "%s%s"%(sort_reverse, col['sort_key'])
                col['img'] = img
        
    return institutions, columns

#### INSTITUTIONAL REPORTS ####
def _get_submissionset_context(request, institution_id, submissionset_id):
    institution = get_object_or_404(Institution, id=institution_id)
    # if no credit set was specified, get the most recent one the user has permission to view.
    if  submissionset_id:
        submissionset = get_object_or_404(SubmissionSet, id=submissionset_id, institution=institution)
        if not (submissionset.is_rated() or request.user.has_perm('view:%s'%institution_id)):
            submissionset = None
    else: # get the latest creditset user has access to
        submissionset = institution.get_latest_submission(request.user.has_perm('view:%s'%institution_id))

    if not submissionset:
        raise PermissionDenied('You do not have access to this submission set report for %s'%institution)

    submission_list = institution.get_submissions(request.user.has_perm('view:%s'%institution_id))
        
    context={'institution': institution,
             'submissionset': submissionset,
             'creditset': submissionset.creditset,
             'submission_list':submission_list}
    return context

@user_can_view
def scorecard(request, institution_id, submissionset_id):
    """
        The overall summary report for an institution
    """
    context = _get_submissionset_context(request, institution_id, submissionset_id)
    
    return respond(request, "institutions/submissionset_scorecard.html", context)


def _get_category_submission_context(request, institution_id, submissionset_id, category_id):
    context = _get_submissionset_context(request, institution_id, submissionset_id)
    category_submission = get_object_or_404(CategorySubmission, submissionset=context.get('submissionset'), category__id=category_id)
            
    context.update({        
        'category': category_submission.category,
        'category_submission': category_submission,
    })
    return context
        
@user_can_view
def category_scorecard(request, institution_id, submissionset_id, category_id):
    """
        The category summary report
    """    
    context = _get_category_submission_context(request, institution_id, submissionset_id, category_id)
    
    return respond(request, "institutions/category_scorecard.html", context)


def _get_subcategory_submission_context(request, institution_id, submissionset_id, category_id, subcategory_id):
    context = _get_category_submission_context(request, institution_id, submissionset_id, category_id)
    
    category_submission=context.get('category_submission')
    subcategory_submission = get_object_or_404(SubcategorySubmission, category_submission=category_submission, subcategory__id=subcategory_id)
                        
    context.update({
        'subcategory': subcategory_submission.subcategory,
        'subcategory_submission': subcategory_submission,
    })
    return context

@user_can_view
def subcategory_scorecard(request, institution_id, submissionset_id, category_id, subcategory_id):
    """
        The sub-category summary report
    """
    context = _get_subcategory_submission_context(request, institution_id, submissionset_id, category_id, subcategory_id)
    
    return respond(request, "institutions/subcategory_scorecard.html", context)


def _get_credit_submission_context(request, institution_id, submissionset_id, category_id, subcategory_id, credit_id):
    context = _get_subcategory_submission_context(request, institution_id, submissionset_id, category_id, subcategory_id)
    
    subcategory_submission = context.get('subcategory_submission')
    credit_submission = get_object_or_404(CreditUserSubmission, subcategory_submission=subcategory_submission, credit__id=credit_id)

    #credit_submission.user = request.user
    
    context.update({
        'credit': credit_submission.credit,
        'credit_submission': credit_submission,
    })
    return context

@user_can_view
def scorecard_credit_detail(request, institution_id, submissionset_id, category_id, subcategory_id, credit_id):
    """
        Detailed report on a single credit.
    """
    context = _get_credit_submission_context(request, institution_id, submissionset_id, category_id, subcategory_id, credit_id)

    return respond(request, "institutions/credit_scorecard.html", context)
