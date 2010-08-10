"""
    apps.helpers.forms Doctests

    Test Premises:
    - this class can be instantiated to process a form
        - with instance (passed via **kwargs)
        - without instance
    
    >>> from stars.apps.helpers.forms.views import FormActionView
    >>> from stars.apps.helpers.forms.models import TestModel
    >>> from django.forms import ModelForm
    >>> from django.db import models
    >>> from django.contrib.auth.models import User
    
    # Initialize Variables
    >>> class TestForm(ModelForm):
    ...  class Meta:
    ...   model = TestModel
    
    >>> test_obj = TestModel(f=False, t=1)
    
    # Dummy Request Object
    >>> class Request(object):
    ...     user = User(username='test')
    ...     def __init__(self, post=None):
    ...         self.set_post(post)
    ...     def set_post(self, post):
    ...         self.POST = post
    ...         if post:
    ...             self.method = 'POST'
    ...         else:
    ...             self.method = "GET"
    
    
    # Test each method

    >>> context_with_instance = {'my_instance': test_obj,}
    >>> context_no_instance = {}
    
    >>> instance_kwargs = {'instance': test_obj}
    
    >>> fav = FormActionView("template.html", TestForm, instance_name='my_instance')
    
    #
    # Test get_context and process_form with a POST request
    #
    >>> r_post = Request()
    >>> r_post.set_post({'f': True, 't': 10})
    
    # >>> context = fav.get_context(r_post, None, **instance_kwargs)
    # >>> context['my_instance']
    # <TestModel: Imma Model>
    # 
    # >>> response = fav.process_form(r_post, context)
    # >>> context['form']
    # <stars.apps.helpers.forms.tests.TestForm object at ...
    # 
    # #
    # # Test get_context and process_form with an empty POST request
    # #
    # 
    >>> r_no_post = Request()
    >>> context = None
    
    # >>> context = fav.get_context(r_no_post, None, **instance_kwargs)
    # >>> context['my_instance']
    # <TestModel: Imma Model>
    # 
    # >>> response = fav.process_form(r_no_post, context)
    # >>> context['form']
    # <stars.apps.helpers.forms.tests.TestForm object at ...
    
    #
    # Test get_context and process_form with a POST request with errors
    #
    
    >>> r_errors = Request()
    >>> r_errors.set_post({'f': True, 't': 'a'})
    >>> context = None
    
    >>> context = fav.get_context(r_errors, None, **instance_kwargs)
    >>> context['my_instance']
    <TestModel: Imma Model>
    
    >>> response = fav.process_form(r_errors, context)
    >>> context['form'].errors['t']
    [u'Enter a whole number.']
    
    #
    # ``get_form_kwargs``
    #
    
    ## w/ instance and no post
    
    >>> fav.get_form_kwargs(r_no_post, context_with_instance)
    {'instance': <TestModel: Imma Model>}
    
    ## w/ instance and post
    >>> dict = fav.get_form_kwargs(r_post, context_with_instance)
    >>> dict['data']['f']
    True
    >>> dict['data']['t']
    10
    >>> dict['instance']
    <TestModel: Imma Model>
    
    ## w/out instance and w/ post
    >>> dict = fav.get_form_kwargs(r_post, context_no_instance)
    >>> dict['data']['f']
    True
    >>> dict['data']['t']
    10
    >>> dict.has_key('instance')
    False
    
    ## w/out instance or post
    >>> fav.get_form_kwargs(r_no_post, context_no_instance)
    {}
    
"""