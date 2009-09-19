from django.forms.forms import BoundField
from django.utils.html import conditional_escape
from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.safestring import mark_safe

from stars.apps.dashboard.credit_editor.forms import ConfirmDelete
from stars.apps.helpers import flashMessage

def object_ordering(request, object_list, form_class, ignore_errors=True, ignore_post=False, ignore_object=False):
    """
        This is a helper function that reduces duplicate code for processing reordering submissions
        It returns a list of (object, ordering form) sets
        the model form should have a __cmp__ function for ordering
        If you are editing more than just the ordering data set ignore_errors to False
        If you want to ignore the post and just get the list use ignore_post
        ignore_object means this object may not have been included in the post, such as a new object
    """
    errors = False
    reordered = False
    object_ordering = []
    parents = set()
    parent_reordered = False
    # save any forms that were submitted for re-ordering
    sorted_list = []
    if request.method == 'POST' and not ignore_post:
        for obj in object_list:
            form = form_class(request.POST, instance=obj, prefix="ordering_%d" % obj.id)
            object_ordering.append({'obj': obj, 'form': form})
            
            if obj != ignore_object:
                if form.is_valid():
                    new_ordinal = int(form.cleaned_data['ordinal'])
                    if new_ordinal != obj.ordinal:
                        obj = form.save()
                        parents.add(obj.get_parent())  # probably the same parent for all objects in the list
                        reordered = True
                else:
                    errors = True
                    # we can safely ignore these errors if ignore_errors, because there is no user input
            sorted_list.append(obj)
        sorted_list.sort()
    else:
        sorted_list = object_list

    if errors:
        flashMessage.send("Unable to update order - Please correct the errors below", flashMessage.ERROR)
    elif reordered:
        flashMessage.send("Order was updated successfully.", flashMessage.SUCCESS)            
        for parent in parents:  # there are just 0 or 1 parents in the set (I think!)
            # Notify the parent object that its child objects have been re-ordered.
            try: 
                parent_reordered = parent.update_ordering()
            except:  # don't worry if object didn't have the required method... just continue on
                pass
    # If the parent was re-ordered, then the objects in the sorted list are out-of-date - reload them
    if parent_reordered:
        sorted_list = object_list._clone()
    
    # create the forms for updating the ordinals
    if not errors or ignore_errors:
        object_ordering = []
        for obj in sorted_list:
            form = form_class(instance=obj, prefix="ordering_%d" % obj.id)
            object_ordering.append({'obj': obj, 'form': form})
    
    return [object_ordering, reordered]

def _get_class_label(klass, method):
    """ Helper: Get a user-friendly label for the given class using the given method name"""
    return getattr(klass, method)() if hasattr(klass, method) else klass.__name__

def _get_form_label(klass):    
    """ Helper: Get a user-friendly label for the given form class """
    return _get_class_label(klass, "form_name")

def _get_model_label(klass):    
    """ Helper: Get a user-friendly label for the given model class """
    return _get_class_label(klass, "model_name")

def _perform_save_form(request, instance, prefix, form_class, save_msg="Changes saved successfully"):
    """
        Helper: for internal use only
        Returns the object form and a saved flag, which is true if the form data was saved to the instance
    """
    saved = False
    if request.method == 'POST':
        object_form = form_class(request.POST, instance=instance, prefix=prefix)
        if object_form.is_valid():
            instance = object_form.save()
            saved = True
            flashMessage.send("%s %s: %s"%(_get_model_label(instance.__class__), instance, save_msg), flashMessage.SUCCESS)
        else:
            flashMessage.send("%s: Please correct the errors below"%_get_form_label(form_class), flashMessage.ERROR)            
    else: 
        object_form = form_class(instance=instance, prefix=prefix)
    return [object_form, instance, saved]
 
#    @todo: get a nice name from the form_class
def basic_save_form(request, instance, prefix, form_class):
    """
        Provides basic form handling for saving an existing model
        Returns the object form and a saved flag, which is true if the form data was saved to the instance
    """
    (object_form, instance, saved) = _perform_save_form(request, instance, prefix, form_class)
    return [object_form, saved]

def basic_save_new_form(request, instance, prefix, form_class):
    """
        Provides basic form handling for saving a new model
        Returns the object form and a saved flag, which is true if the form data was saved to the instance
    """
    (object_form, instance, saved) = _perform_save_form(request, instance, prefix, form_class, save_msg="Created successfully")
    if saved:
        try:  # Notify the parent object that a new child object was just added.
            instance.get_parent().update_ordering()
        except:  # if parent didn't have an update_ordering method, no worries!
            pass
    return [object_form, saved]

def confirm_delete_form(request, instance, delete_method=None):
    """
        Provides basic form handling for confirming and deleting an existing model
        Uses instance.delete() to perform the deletion if no delete_method is supplied
        Returns (form, deleted), where form is the delete confirmation form and deleted is True if the form was POST'ed and the deletion performed successfully.
    """
    deleted = False
    if not delete_method:
        delete_method = instance.delete
    if request.method == "POST":
        form = ConfirmDelete(request.POST)
        if form.is_valid():
            if form.cleaned_data['confirm']:
                msg_parms = (_get_model_label(instance.__class__), unicode(instance))
                delete_method()
                flashMessage.send("%s %s was deleted."%msg_parms, flashMessage.SUCCESS)
                deleted = True
    else:
        form = ConfirmDelete()
    form.instance = instance
    return (form, deleted)

def confirm_delete_and_update_form(request, instance, delete_method=None):
    """
        Exactly as above, but calls instance.delete_and_update() to perform the deletion.
    """
    return confirm_delete_form(request, instance, instance.delete_and_update)
           
#  Not used anywhere (AFAICT) and duplicates work of form rendering templates    
#def two_column_layout(form):
#    """
#        Helper function that displays a form in two columns
#        mostly copied from django.forms.forms.py
#        _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
#    """
#    # My additions
#    left_column_row = u'<tr><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td>'
#    right_column_row = u'<th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s</td></tr>'
#    end_odd_row = u"</tr>"
#    error_row = u'<li>%s</li>'
#    row_ender = u"</td></tr>"
#    errors_on_separate_row = False
#    help_text_html = u'<br />%s'
#    error_row = u'<tr><td colspan="4">%s</td></tr>'
#    
#    top_errors = form.non_field_errors() # Errors that should be displayed above all fields.
#    output, hidden_fields = [], []
#    counter = 0
#    for name, field in form.fields.items():
#        bf = BoundField(form, field, name)
#        bf_errors = form.error_class([conditional_escape(error) for error in bf.errors]) # Escape and cache in local variable.
#        if bf.is_hidden:
#            if bf_errors:
#                top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
#            hidden_fields.append(unicode(bf))
#        else:
#            if bf.label:
#                label = conditional_escape(force_unicode(bf.label))
#                # Only add the suffix if the label does not end in
#                # punctuation.
#                if form.label_suffix:
#                    if label[-1] not in ':?.!':
#                        label += form.label_suffix
#                label = bf.label_tag(label) or ''
#            else:
#                label = ''
#            if field.help_text:
#                help_text = help_text_html % force_unicode(field.help_text)
#            else:
#                help_text = u''
#            if counter % 2 == 0:
#                output.append(left_column_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
#            else:
#                output.append(right_column_row % {'errors': force_unicode(bf_errors), 'label': force_unicode(label), 'field': unicode(bf), 'help_text': help_text})
#            counter += 1
#    if counter % 2:
#        output[-1] += end_odd_row
#    if top_errors:
#        output.insert(0, error_row % force_unicode(top_errors))
#    if hidden_fields: # Insert any hidden fields in the last row.
#        str_hidden = u''.join(hidden_fields)
#        if output:
#            last_row = output[-1]
#            # Chop off the trailing row_ender (e.g. '</td></tr>') and
#            # insert the hidden fields.
#            #if not last_row.endswith(row_ender):
#                # This can happen in the as_p() case (and possibly others
#                # that users write): if there are only top errors, we may
#                # not be able to conscript the last row for our purposes,
#                # so insert a new, empty row.
#                #last_row = left_column_row % {'errors': '', 'label': '', 'field': '', 'help_text': ''}
#                #output.append(last_row)
#            output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
#        else:
#            # If there aren't any rows in the output, just append the
#            # hidden fields.
#            output.append(str_hidden)
#    return mark_safe(u'\n'.join(output))