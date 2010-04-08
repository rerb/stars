"""
    apps.helpers.forms Doctests

    Test Premises:
    - this class can be instantiated to process a form w/out a model
    - ... w/ a model
    
    >>> from stars.apps.helpers.forms.views import FormActionView
    >>> from stars.apps.helpers.forms.models import TestModel
    >>> from django.forms import ModelForm
    >>> from django.db import models
    >>> from django.contrib.auth.models import User
    
    # Initialize Variables
    >>> class TestForm(ModelForm):
    ...  class Meta:
    ...   model = TestModel
    
    >>> test_model = TestModel(f=False)
    
    # Dummy Request Object
    >>> class Request(object):
    ...     def __init__(self, post=None):
    ...         self.set_post(post)
    ...     def set_post(self, post):
    ...         self.POST = post
    ...         if post:
    ...             self.method = 'POST'
    ...         else:
    ...             self.method = "GET"
    
    
    # Test each method
    
    # ``init``
    
    # w/ Model
    >>> fav_model = FormActionView("template.html", TestForm, instance=test_model)
    
    # w/out Model
    >>> fav_no_model = FormActionView("template.html", TestForm)
    
    # ``get_form_kwargs``
    
    # w/ model
    
    # w/out post
    >>> r = Request()
    
    >>> fav_model.get_form_kwargs(r)
    {'instance': <TestModel: Imma Model>}
    
    # w/ post
    >>> r.set_post({'f': True, 't': 10})
    >>> dict = fav_model.get_form_kwargs(r)
    >>> dict['instance']
    <TestModel: Imma Model>
    >>> dict['data']['f']
    True
    >>> dict['data']['t']
    10
    
    # w/out model
    
    # w/out Post
    >>> r.set_post(None)
    >>> fav_no_model.get_form_kwargs(r)
    {}
    
    # w/ post
    >>> r.set_post({'f': True, 't': 10})
    >>> dict = fav_no_model.get_form_kwargs(r)
    >>> dict['data']['f']
    True
    >>> dict['data']['t']
    10

    # ``process_form``
    
    # w/ model
    
    # w/ post
    # If it validates `process_form` will return a redirect
    >>> r.set_post({'f': False, 't': 11})
    >>> fav_model.context_dict.has_key('form')
    False
    >>> fav_model.process_form(r)
    <django.http.HttpResponseRedirect object at ...
    
    # Make sure that `process_form` adds 'form' to the context
    >>> fav_model.context_dict['form']
    <stars.apps.helpers.forms.tests.TestForm object at ...
    >>> fav_model.instance.f
    False
    >>> fav_model.instance.t
    11
    
    # w/out post
    
    >>> r.set_post(None)
    >>> fav_model.process_form(r)
    >>> fav_model.context_dict['form']
    <stars.apps.helpers.forms.tests.TestForm object at ...
    >>> fav_model.instance.f
    False
    >>> fav_model.instance.t
    11
    
    # w/out model
    
    # w/out post
    >>> fav_no_model.process_form(r)
    >>> fav_model.context_dict['form']
    <stars.apps.helpers.forms.tests.TestForm object at ...
    
    # w/ post
    >>> r.method = "POST"
    >>> r.set_post({'f': True, 't': 12})
    
    # No model = no redirect
    >>> fav_no_model.process_form(r)
    
    # w/out ``IntegerField``
    >>> r.set_post({'f': True})
    >>> fav_model.process_form(r)
    <django.http.HttpResponseRedirect object at ...
    >>> fav_model.context_dict['form'].errors
    {}
    
    # w/ error for ``t`` value
    >>> r.set_post({'f': True, 't': 'a'})
    
    # No response from process_form since there are errors
    >>> fav_model.process_form(r)
    >>> fav_model.context_dict['form'].errors
    {'t': [u'Enter a whole number.']}
    
    # Confirm ``process_form`` raises a RedirectException
    # when ``get_success_redirect`` returns a value
    # @ Todo

    # ``get_context``
    
    # w/ model
    
    >>> r.user = User()
    >>> fav_model = FormActionView("template.html", TestForm, instance=test_model)
    >>> request_context = fav_model.get_context(r)
    >>> fav_model.context_dict['testmodel']
    <TestModel: Imma Model>
    
    # w/out Model
    >>> del(fav_no_model)
    >>> fav_no_model = FormActionView("template.html", TestForm)
    >>> request_context = fav_no_model.get_context(r)
    >>> fav_no_model.instance
    >>> fav_no_model.context_dict.has_key('testmodel')
    False
    
"""