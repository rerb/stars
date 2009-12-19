from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404

from stars.apps.auth.utils import respond
from stars.apps.auth import utils as auth_utils
from stars.apps.auth.decorators import user_is_staff
from stars.apps.helpers import flashMessage
from stars.apps.helpers.forms import form_helpers
from stars.apps.institutions.models import Institution
from stars.apps.tool.manage.forms import AdminEnableInstitutionForm
from stars.apps.submissions.models import Payment
from stars.apps.tool.admin.forms import PaymentForm
from stars.apps.cms.models import ArticleCategory, articleCategories_sync, articleCategories_perform_consistency_check

@user_is_staff
def institutions_search(request):
    """
        Provides a search page for Institutions
    """
    return respond(request, 'tool/admin/institutions/institution_search.html', {})

@user_is_staff
def institutions_list(request):
    """
        A list of latest submissionsets for ALL registered institutions currently participating in STARS.
    """
    institutions = Institution.objects.order_by('-state__active_submission_set__date_registered')
    saved = False
    
    # Add the latest submission set and payment to each institution
    for institution in institutions:
        institution.enable_form, form_saved = form_helpers.basic_save_form(request, institution, 'enable_%s'%institution.id, AdminEnableInstitutionForm,  flash_message=False)
        saved = saved or form_saved
        institution.submission_set = institution.get_latest_submission(True)
        if institution.submission_set:
            payments = institution.submission_set.payment_set.order_by('-date')
            institution.payment = payments[0] if payments else None
        
    if saved:
        flashMessage.send("Institutions updated successfully.", flashMessage.SUCCESS)
    if institution:
        enable_help_text = institution.enable_form['enabled'].help_text

    template = "tool/admin/institutions/institution_list.html"
    return respond(request, template, {'institution_list':institutions, 'enable_help_text':enable_help_text})
    
@user_is_staff
def find_institution_gateway(request, snippet):
    """
        Searches stars_member_list.members for any school that includes
        the snippet in its name
        @Todo: sync with ISS DB when it comes online
    """
    institution_list = Institution.find_institutions(snippet)
    return render_to_response('tool/admin/institutions/search_results.html', {'institution_list': institution_list})
    
@user_is_staff
def select_institution(request, institution_id):
    """
        The admin tool for selecting a particular institution from stars_member_list.members
    """
    institution = Institution.load_institution(institution_id)
    if not institution:
        raise Http404("No such institution.")
    
    if auth_utils.change_institution(request, institution):  
        redirect_url = request.GET.get('redirect', settings.MANAGE_INSTITUTION_URL) 
        response = HttpResponseRedirect(redirect_url)
        # special hack to "remember" current institution for staff between sessions
        #  - can't store it in session because it gets overwritten on login, can's store it with account b/c staff don't have accounts.
        #  - ideally, the cookie path would be LOGIN_URL, but the first request we get is from the login redirect url.
        response.set_cookie("current_inst", institution.aashe_id, path=settings.LOGIN_REDIRECT_URL)
        return response
    else:
        flashMessage.send("Unable to change institution to %s - check the log?"%institution, flashMessage.ERROR)
        return HttpResponseRedirect(settings.ADMIN_URL)
    
@user_is_staff
def articles(request):
    """
        Provides utilities and links for managing CMS articles and categories
    """
    category_table, is_consistent = articleCategories_perform_consistency_check()
    context = {"category_table" : category_table, "is_consistent" : is_consistent}
    template = "tool/admin/cms/articles.html"
    return respond(request, template, context)
    

# @todo: use Django's built-in caching to do this 
@user_is_staff
def article_category_sync(request):
    """ Synchronize the article categories with the IRC (cache refresh)"""
    # clear the cms_articlecategory table
    for cat in ArticleCategory.objects.all() :
            cat.delete()    
            
    errors = articleCategories_sync()
    category_table, is_consistent = articleCategories_perform_consistency_check()
    
    context = {"category_table" : category_table, "is_consistent" : is_consistent, "error_list" : errors}
    template = "tool/admin/cms/article_category_sync.html"
    return respond(request, template, context)

@user_is_staff
def payments(request):
    """
        A list of institution payments
    """
    institutions = Institution.objects.all()

    # Add the latest submission set and payment to each institution...
    for institution in institutions:
        institution.submission_set = None
        institution.payment = None
        submissions = institution.submissionset_set.order_by('-date_registered')
        if submissions:
            institution.submission_set = submissions[0]
            payments = institution.submission_set.payment_set.order_by('-date')
            if payments:
                institution.payment = payments[0]
        print "Submission Set: %s, Payment: %s"%(institution.submission_set, institution.payment)
    template = "tool/admin/payments/list.html"
    return respond(request, template, {'institution_list':institutions})
    
@user_is_staff
def edit_payment(request, payment_id):
    """
        Edit a particular payment
    """
    payment = get_object_or_404(Payment, pk=payment_id)
    object_form, status = form_helpers.basic_save_form(request, payment, "payment", PaymentForm)
    
    template = "tool/admin/payments/edit.html"
    return respond(request, template, {'payement': payment, 'object_form': object_form})