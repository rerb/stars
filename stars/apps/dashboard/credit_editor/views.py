from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
#from django import db # FOR TESTING ONLY

from stars.apps.auth.utils import respond
from stars.apps.auth.decorators import user_is_staff
from stars.apps.credits.models import *
from stars.apps.submissions.models import CreditTestSubmission
from stars.apps.helpers.forms import form_helpers
from stars.apps.helpers.forms.forms import HiddenCounterForm
from stars.apps.helpers import flashMessage
from stars.apps.dashboard.credit_editor.forms import *

@user_is_staff
def home(request):
    """
        Forwards the user to the latest version.
    """
    # simply forward the visitor to the latest version
    latest_version = CreditSet.objects.all()[0]
    return HttpResponseRedirect(latest_version.get_edit_url())
    
############### CREDIT-SET CRUD ######################
def _get_creditset_context(creditset_id):
    # confirm that the credit set exists
    creditset = get_object_or_404(CreditSet, id=creditset_id)
    context = {
        'creditset': creditset,
        'available_sets': CreditSet.objects.all(),
    }
    return context

@user_is_staff
def credit_set_detail(request, creditset_id):
    """
        Shows the summary page for a specific CreditSet
    """
    context = _get_creditset_context(creditset_id)
    creditset = context['creditset']
        
    # Build and process the form for the creditset
    (object_form, saved) = form_helpers.basic_save_form(request, creditset, 'cs_%d' % creditset.id, CreditSetForm)
        
    # Build the form for adding a new category
    new_category_form = CategoryForm(prefix='new_cat')
        
    # Build and process the forms for ordering the categories
    (object_ordering, reordered) = form_helpers.object_ordering(request, creditset.category_set.all(), CategoryOrderForm)
            
    template = "dashboard/credit_editor/set_detail.html"
    context.update({'object_form': object_form, 
                    'object_ordering': object_ordering, 
                    'new_category_form': new_category_form,
    })
    return respond(request, template, context)
    
@user_is_staff
def add_credit_set(request):
    """
        Provides and processes a form for adding a new Credit Set
    """
    # Build and process the form for adding a new category
    new_creditset = CreditSet()
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_creditset, 'new_cs', CreditSetForm)
    if saved:
        return HttpResponseRedirect(new_creditset.get_edit_url())

    template = 'dashboard/credit_editor/new_creditset.html'
    context = {
        'object_form': object_form,
        'available_sets': CreditSet.objects.all(),
    }
    return respond(request, template, context)
    
############### CATEGORY CRUD ######################
def _get_category_context(creditset_id, category_id):
    context = _get_creditset_context(creditset_id)
    # confirm that the category exists
    category = get_object_or_404(Category, id=category_id, creditset=context['creditset'])
    context.update({'category': category})
    return context

@user_is_staff
def category_detail(request, creditset_id, category_id):
    """
        Shows the details for a particular category
    """
    context = _get_category_context(creditset_id, category_id)
    category = context['category']
           
    # Build the form for adding a new subcategory
    new_subcategory_form = NewSubcategoryForm(prefix='new_subcat')
        
    # Build and process the form for the category
    (object_form, saved) = form_helpers.basic_save_form(request, category, 'cat_%d' % category.id, CategoryForm)
    
    # Build and process the form for ordering subcategories
    (object_ordering, reordered) = form_helpers.object_ordering(request, category.subcategory_set.all(), SubcategoryOrderForm)
    
    template = "dashboard/credit_editor/category.html"
    context.update({'object_form': object_form, 
                    'object_ordering': object_ordering, 
                    'new_subcategory_form': new_subcategory_form,
    })
    return respond(request, template, context)
    
@user_is_staff
def delete_category(request, creditset_id, category_id):
    """
        Shows a confirmation form to remove a category
    """
    context = _get_category_context(creditset_id, category_id)
    category = context['category']
        
    (form, deleted) = form_helpers.confirm_delete_form(request, category)       
    if deleted:
        return HttpResponseRedirect(context['creditset'].get_edit_url())
                
    template = "dashboard/credit_editor/delete_object.html"
    context.update({'object_class':'Category', 'object':category, 'confirm_delete_form': form, 'dependent_depth': 3})
    return respond(request, template, context)
    
@user_is_staff
def add_category(request, creditset_id):
    """
        This view provides and processes a form to edit a new category
    """
    context = _get_creditset_context(creditset_id)
    
    # Build and process the form for adding a new category
    new_category = Category(creditset=context['creditset'])
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_category, 'new_cat', CategoryForm)
    if saved:
        return HttpResponseRedirect(new_category.get_edit_url())
    
    template = 'dashboard/credit_editor/new_category.html'
    context.update({"object_form": object_form})
    return respond(request, template, context)
    
############### SUB-CATEGORY CRUD ######################
def _get_subcategory_context(creditset_id, category_id, subcategory_id):
    context = _get_category_context(creditset_id, category_id)
    # confirm that the subcategory exists
    subcategory = get_object_or_404(Subcategory, id=subcategory_id, category=context['category'])
    context.update({'subcategory': subcategory})
    return context

@user_is_staff
def subcategory_detail(request, creditset_id, category_id, subcategory_id):
    """
        Shows the details for a particular subcategory
    """
    context = _get_subcategory_context(creditset_id, category_id, subcategory_id)
    subcategory = context['subcategory']
        
   # Build the form for adding a new subcategory
    new_credit_form = NewCreditForm(prefix='new_credit')
            
    # Build and process the form for the subcategory
    (object_form, saved) = form_helpers.basic_save_form(request, subcategory, 'subcat_%d' % subcategory.id, SubcategoryForm)
        
    # Build and process the form for ordering credits
    (object_ordering, reordered) = form_helpers.object_ordering(request, subcategory.credit_set.all(), CreditOrderForm)
    # if the credits were re-ordered, then our queryset is out of date - get a new one.
    if reordered:
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)

    # Check for a changed Category
    if subcategory.category != context['category']:
        # update the numbers
        subcategory.category.update_ordering()
        context['category'].update_ordering()
        return HttpResponseRedirect(subcategory.get_edit_url())
    
    template = "dashboard/credit_editor/subcategory.html"
    context.update({'subcategory': subcategory,  # overwrite subcategory in case it was re-ordered.
                    'object_form': object_form, 
                    'object_ordering': object_ordering,
                    'new_credit_form': new_credit_form, 
    })
    return respond(request, template, context)
    
@user_is_staff
def delete_subcategory(request, creditset_id, category_id, subcategory_id):
    """
        Shows a confirmation form to remove a subcategory
    """
    context = _get_subcategory_context(creditset_id, category_id, subcategory_id)
    subcategory = context['subcategory']
        
    # Confirm the deletion and re-order credits in this category
    (form, deleted) = form_helpers.confirm_delete_and_update_form(request, subcategory)       
    if deleted:
        return HttpResponseRedirect(context['category'].get_edit_url())
                
    template = "dashboard/credit_editor/delete_object.html"
    context.update({'object_class':'Subcategory', 'object':subcategory, 'confirm_delete_form': form, 'dependent_depth': 2})
    return respond(request, template, context)
    
@user_is_staff
def add_subcategory(request, creditset_id, category_id):
    """
        This view provides and processes a form to edit a new subcategory
    """
    context = _get_category_context(creditset_id, category_id)

    # Build and precess the form for adding a new category
    new_subcategory = Subcategory(category=context['category'])

    (object_form, saved) = form_helpers.basic_save_new_form(request, new_subcategory, 'new_subcat', NewSubcategoryForm)
    if saved:
        return HttpResponseRedirect(new_subcategory.get_edit_url())

    template = 'dashboard/credit_editor/new_subcategory.html'
    context.update({"object_form": object_form})
    return respond(request, template, context)
    
############### CREDIT CRUD ######################
def _get_credit_context(creditset_id, category_id, subcategory_id, credit_id):
    context = _get_subcategory_context(creditset_id, category_id, subcategory_id)
    # confirm that the credit exists
    credit = get_object_or_404(Credit, id=credit_id, subcategory=context['subcategory'])    
    context.update({"credit": credit})
    return context

@user_is_staff
def credit_detail(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Show the details for a particular credit and provides editing forms
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']
    
    # Build and process the form for the credit
    (object_form, saved) = form_helpers.basic_save_form(request, credit, 'credit_%d' % credit.id, CreditForm)
    
    # Check for a changed subcategory
    if credit.subcategory != context['subcategory']:
        credit.subcategory.category.update_ordering()
        context['subcategory'].category.update_ordering()
        return HttpResponseRedirect(credit.get_edit_url())
    
    template = 'dashboard/credit_editor/credits/detail.html'
    context.update({"object_form": object_form})
    return respond(request, template, context)

@user_is_staff
def delete_credit(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Shows a confirmation form to remove a credit
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)

    (form, deleted) = form_helpers.confirm_delete_and_update_form(request, context['credit'])       
    if deleted:
        return HttpResponseRedirect(context['subcategory'].get_edit_url())
                
    template = "dashboard/credit_editor/delete_object.html"
    context.update({'object_class':'Credit', 'object':context['credit'], 'confirm_delete_form': form})
    return respond(request, template, context)
    
@user_is_staff
def add_credit(request, creditset_id, category_id, subcategory_id):
    """
        The view where users can create a credit
    """
    context = _get_subcategory_context(creditset_id, category_id, subcategory_id)

    # Build and process the form for adding a new category
    new_credit = Credit(subcategory=context['subcategory'])

    (object_form, saved) = form_helpers.basic_save_new_form(request, new_credit, 'new_credit', NewCreditForm)
    if saved:
        return HttpResponseRedirect(new_credit.get_edit_url())

    template = 'dashboard/credit_editor/new_credit.html'
    context.update({"object_form": object_form})
    return respond(request, template, context)
    
############### CREDIT DOCUMENTATION FIELDS ######################
def _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id):
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    # confirm that the credit exists
    # confirm that the documentation field exists
    field = get_object_or_404(DocumentationField, id=field_id, credit=context['credit'])
    context.update({'field': field})
    return context

@user_is_staff
def credit_fields(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Show the documentation fields for a particular credit and provides editing forms
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']
    
    # Build and process the form for adding a new field
    new_field_form = NewDocumentationFieldForm(prefix='new_field')
    
    # Build and process the form for ordering fields
    (object_ordering, reordered) = form_helpers.object_ordering(request, credit.documentationfield_set.all(), DocumentationFieldOrderingForm)
    
    template = 'dashboard/credit_editor/credits/fields.html'
    context.update({'object_ordering': object_ordering,
                    'object_form': new_field_form,
    })
    return respond(request, template, context)

@user_is_staff
def add_field(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Provides and processes a form for adding a new documentation field
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
            
    new_field = DocumentationField(credit=context['credit'])
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_field, 'new_field', NewDocumentationFieldForm)
    if saved:
        return HttpResponseRedirect(new_field.get_edit_url())
    
    template = 'dashboard/credit_editor/credits/new_field.html'
    context.update({"object_form": object_form})
    return respond(request, template, context)
    
@user_is_staff
def field_detail(request, creditset_id, category_id, subcategory_id, credit_id, field_id):
    """
        Provides a set of forms to edit a Documentation Field
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
    field = context['field']
            
    # Build and process the form for the field
    (field_form, saved) = form_helpers.basic_save_form(request, field, 'field_%d' % field.id, DocumentationFieldForm)
    
    # @todo: If the type field changed, check if there are any submissions affected and redirect to a warning view if so.
    #        The warning view should list the affected submissions, modify them (remove choice and reset status), and then re-direct here
    #        But how to keep track of the original POST data in the mean time???

    # An arbitrary number of new choices may have been added to the choice ordering form - save the choices.
    (new_choices, new_choice_errors) = \
          form_helpers.save_new_form_rows(request, 'ordering', ChoiceForm, Choice, documentation_field=field)
    # Set-up an empty choice form for adding another choice...
    new_choice_form = ChoiceForm(instance=Choice(documentation_field = field), prefix='ordering_new0')
    
    # Build the form for editing and ordering choices - this form is processed by a custom view to avoid interfering with custom validation on the object_form above.
    choices = field.choice_set.filter(is_bonafide=True)
    (object_ordering, reordered) = form_helpers.object_ordering(request, choices, ChoiceOrderingForm, ignore_errors=not field.is_choice() or new_choice_errors, ignore_objects=new_choices)
        
    template = 'dashboard/credit_editor/credits/field_detail.html'
    context.update({'field_form': field_form,
                    'object_ordering': object_ordering,
                    'new_choice_form': new_choice_form,
                    'hidden_counter_form': HiddenCounterForm(),  # always start with an unbound counter form.
                    'choice_state':'expanded' if field.is_choice() else 'hidden',
                    'field_help_state':'collapsed' if field.inline_help_text or field.tooltip_help_text else 'expanded',
                   })
    return respond(request, template, context)

@user_is_staff
def delete_field(request, creditset_id, category_id, subcategory_id, credit_id, field_id):
    """
        Deletes a selected Documentation Field
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
                
    (form, deleted) = form_helpers.confirm_delete_form(request, context['field'])       
    if deleted:
        return HttpResponseRedirect("%sfields/" % context['credit'].get_edit_url())
    
    template = 'dashboard/credit_editor/credits/delete_field.html'
    context.update({'object_class':'Reporting Field', 'object':context['field'],'confirm_delete_form': form,})
    return respond(request, template, context)

############### DOCUMENTATION FIELD CHOICES ######################    
@user_is_staff
def add_choice(request, creditset_id, category_id, subcategory_id, credit_id, field_id):
    """
        Provides and processes a form for adding a new choice to a documentation field
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
    field = context['field']
    new_choice = Choice(documentation_field=field)
    
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_choice, 'new_choice', ChoiceForm)

    return HttpResponseRedirect("%s?expand_choices=True"%field.get_edit_url())    

@user_is_staff
def edit_choice(request, creditset_id, category_id, subcategory_id, credit_id, field_id, choice_id):
    """
        Edit a choice - allows the choice wording to change without affecting submissions using this choice.
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
    field = context['field']

    choice = get_object_or_404(Choice, id=choice_id, documentation_field = field)
    (object_form, saved) = form_helpers.basic_save_form(request, choice, 'choice', ChoiceForm)
    if saved:
        return HttpResponseRedirect("%s?expand_choices=True"%field.get_edit_url())    
    
    template = 'dashboard/credit_editor/credits/choice_detail.html'
    context.update({'choice':choice, 'object_form': object_form})
    return respond(request, template, context)

@user_is_staff
def reorder_choices(request, creditset_id, category_id, subcategory_id, credit_id, field_id):
    """
        Handles a re-order post for Documentation Field - which has custom validation - messed up by the order-form post
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
    field = context['field']
                
    # Build and process the form for ordering choices
    (object_ordering, reordered) = form_helpers.object_ordering(request, field.choice_set.filter(is_bonafide=True), ChoiceOrderingForm)

    return HttpResponseRedirect("%s?expand_choices=True"%field.get_edit_url())    
    
@user_is_staff
def delete_choice(request, creditset_id, category_id, subcategory_id, credit_id, field_id, choice_id):
    """
        Provides and processes a form for deleting a choice from a documentation field
    """
    context = _get_doc_field_context(creditset_id, category_id, subcategory_id, credit_id, field_id)
    field = context['field']

    # confirm that the choice exists, and confirm that it should really be deleted, along with any submissions refering to it!
    choice = get_object_or_404(Choice, id=choice_id, documentation_field = field)
    (form, deleted) = form_helpers.confirm_delete_form(request, choice)
    if deleted:
        return HttpResponseRedirect("%s?expand_choices=True"%field.get_edit_url())    
    
    #@todo: rename the delete form to make it more generic - and override Choice.delete() to manage the submission objects.
    template = 'dashboard/credit_editor/credits/applicability_delete.html'
    context.update({'object_class':'Choice', 'object':choice,'confirm_delete_form': form,})
    return respond(request, template, context)

############### CREDIT APPLICABILITY REASONS ######################    
@user_is_staff
def credit_applicability(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Show the applicability reasons for a particular credit
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']
    # create the form for editing an Applicability Reason
    new_reason = ApplicabilityReason(credit=credit)
    (object_form, saved) = form_helpers.basic_save_new_form(request, new_reason, 'new_reason', ApplicabilityReasonForm)
    if saved:
        return HttpResponseRedirect(new_reason.get_absolute_url())
    
    reason_list = ApplicabilityReason.objects.filter(credit = credit)
    template = 'dashboard/credit_editor/credits/applicability.html'
    context.update({'object_form': object_form,
                    'object_edit_list': reason_list,
                   })
    return respond(request, template, context)

@user_is_staff
def edit_applicability(request, creditset_id, category_id, subcategory_id, credit_id, reason_id):
    """
        Edit an applicability reason
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']    

    reason = get_object_or_404(ApplicabilityReason, id=reason_id, credit=credit)
    (object_form, saved) = form_helpers.basic_save_form(request, reason, 'reason', ApplicabilityReasonForm)
    if saved:
        return HttpResponseRedirect(reason.get_absolute_url())
    
    template = 'dashboard/credit_editor/credits/applicability_detail.html'
    context.update({'reason':reason, 'object_form': object_form})
    return respond(request, template, context)
    
@user_is_staff
def delete_applicability(request, creditset_id, category_id, subcategory_id, credit_id, reason_id):
    """
        Delete an applicability reason
    """
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']    
    # confirm the applicability reason exists and delete it
    reason = get_object_or_404(ApplicabilityReason, id=reason_id, credit=credit)
    (form, deleted) = form_helpers.confirm_delete_form(request, reason)
    if deleted:
        return HttpResponseRedirect(reason.get_absolute_url())
    
    template = 'dashboard/credit_editor/credits/applicability_delete.html'
    context.update({'object_class':'Applicability Reason', 'object':reason,'confirm_delete_form': form,})
    return respond(request, template, context)
    

############### CREDIT FORMULA (with custom VALIDATION) and TEST CASES ######################
def _get_credit_formula_context(creditset_id, category_id, subcategory_id, credit_id):
    context = _get_credit_context(creditset_id, category_id, subcategory_id, credit_id)
    # Retrieve the list of documentation fields for this credit
    fields = context['credit'].documentationfield_set.all()
    context.update({'documentation_fields': fields})
    return context

@user_is_staff
def credit_formula(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Edit the formula and validation rules along with test data for a particular credit
    """
    context = _get_credit_formula_context(creditset_id, category_id, subcategory_id, credit_id)
    credit = context['credit']
        
    # Build, validate, and process the form for the credit formula
    (formula_form, saved) = form_helpers.basic_save_form(request, credit, 'credit_%d' % credit.id, CreditFormulaForm)

    # Display the formula test suite and New Test form...
    #    Delicately trying to handle several cases here:
    #    - GET: new credit, no formula entered yet - Don't show test suite 
    #    - GET: existing formula compiles - Show test suite
    #    - POST: formula error - Don't show test suite
    #    - POST: formula compiles - Show test suite
    test_case_list = [] 
    new_test_form = None
    if credit.formula and (request.method == 'GET' or formula_form.is_valid()):  # don't do this if the formula was not valid, otherwise message applies to credit's old formula rather than current formula on form
        (compiled, message) = credit.compile_formula()
        if not compiled or request.method == 'POST' :
            flashMessage.send( message, flashMessage.NOTICE if compiled else flashMessage.ERROR )
        if compiled:
            # Retrieve any existing test cases for this credit, only if the formula compiles
            test_case_list = CreditTestSubmission.objects.filter(credit = credit)
            for test_case in test_case_list:
                test_case.run_test()
        
            # Build the form for adding a new test case
            new_test_case = CreditTestSubmission(credit=credit)
            new_test_form = CreditTestSubmissionForm(instance=new_test_case, prefix='test_case')

    # compile the validation rules
    if credit.validation_rules and (request.method == 'GET' or formula_form.is_valid()):
        (success, message) = credit.compile_validation_rules()
        if not success or request.method == 'POST' :
            flashMessage.send( message, flashMessage.NOTICE if success else flashMessage.ERROR )

    template = 'dashboard/credit_editor/credits/formula.html'
    context.update({'object_form': formula_form,
                    'object_edit_list': test_case_list,
                    'submission_form': new_test_form,
    })
    return respond(request, template, context)
    
@user_is_staff
def formula_test_case(request, creditset_id, category_id, subcategory_id, credit_id, test_case_id):
    """
        Provides a form to edit a Credit Formula Test Case
    """
    context = _get_credit_formula_context(creditset_id, category_id, subcategory_id, credit_id)
    
    # confirm that the test case exists
    test_case = get_object_or_404(CreditTestSubmission, id=test_case_id, credit=context['credit'])
    
    # Build and process the form for the test case
    (test_case_form, saved) = form_helpers.basic_save_form(request, test_case, 'test_case', CreditTestSubmissionForm)
     
    # don't run test if the form had errors...  
    test_case.reset_test()
    if request.method == 'GET' or test_case_form.is_valid():
        (had_error, message) = test_case.run_test()
        if (had_error):
            flashMessage.send(message, flashMessage.ERROR)
           
    template = 'dashboard/credit_editor/credits/formula_test_case.html'
    context.update({'test_case': test_case,
                    'submission_form': test_case_form,
    })
    return respond(request, template, context)

@user_is_staff
def add_formula_test_case(request, creditset_id, category_id, subcategory_id, credit_id):
    """
        Provides and processes a form for adding a new credit formula test case
    """
    context = _get_credit_formula_context(creditset_id, category_id, subcategory_id, credit_id)
        
    # Build and process the form for adding a new test case
    new_test_case = CreditTestSubmission(credit=context['credit'])
    (new_test_form, saved) = form_helpers.basic_save_new_form(request, new_test_case, 'test_case', CreditTestSubmissionForm)   
    if saved:
        return HttpResponseRedirect(new_test_case.get_edit_url())

    template = 'dashboard/credit_editor/credits/new_test_case.html'
    context.update({'test_case': new_test_case,
                    'submission_form': new_test_form,
    })
    return respond(request, template, context)
    
@user_is_staff
def delete_formula_test_case(request, creditset_id, category_id, subcategory_id, credit_id, test_case_id):
    """
        Deletes a selected Credit Forumla Test Case
    """
    context = _get_credit_formula_context(creditset_id, category_id, subcategory_id, credit_id)
    
    # confirm that the test case field exists, then delete it (confirmed on client=side)
    test_case = get_object_or_404(CreditTestSubmission, id=test_case_id, credit=context['credit'])
    test_case.delete()           
    flashMessage.send("Formula Test Case was deleted.", flashMessage.SUCCESS)

    return HttpResponseRedirect("%s" % context['credit'].get_formula_url())
