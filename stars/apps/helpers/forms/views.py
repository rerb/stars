from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from stars.apps.auth.decorators import _redirect_to_login
from stars.apps.helpers import flashMessage

import sys

# class RedirectException(Exception):
#        def __init__(self, url):
#            self.url = url
#        def __str__(self):
#            return repr("Redirect: " % self.url)

class TemplateView(object):
    """
        A generic class view that all other views can extend
    """
    def __init__(self, template, context={}):
        self.template = template
        self.context = context

    def __call__(self, request, *args, **kwargs):
        """ Simply calls render """
        return self.render(request, *args, **kwargs)

    def render(self, request, *args, **kwargs):
        """ Renders the response """
        return render_to_response(self.template, self.get_context(request))
        
    def get_context(self, request, context={}):
        """ Add/update any context variables """
        _context = {}
        self.context.update(_context)
        return self.context
    
class FormActionView(object):
    """
        This callable class can be extended to handle any form submission
    """
    
    def __init__(self, template, formClass, instance=None, has_upload=False, form_name='form', instance_name=None, init_context=None):
        """ Initializes the class with a formclass and template """
        self.formClass = formClass
        self.template = template
        self.instance = instance
        self.has_upload = has_upload
        self.form_name = form_name
        self.instance_name = instance_name
        if not init_context:
            self.context_dict = {}
        else:
            self.context_dict = init_context
    
    def __call__(self, request, instance=None):
        """ Call the class as if it were a function """
        
        if not instance:
            self.get_instance(request)
        else:
            self.instance = instance
        
        return self.render(request)
        
    def render(self, request, *args, **kwargs):
        """ Where all the work is done """
        
        response = self.process_form(request)
        if response:
            return response
            
        return render_to_response(self.template, self.get_context(request))
        
    def get_instance(self, request):
        """ Provides a way for the class to get the model instance from the request object """
        return self.instance
        
    def get_context(self, request):
        """ Adding any additional context items to the context. Uses ``RequestContext`` """
        
        self.context_dict.update(self.get_extra_context(request))

        if self.instance:
            if self.instance_name:
                self.context_dict[self.instance_name] = self.instance
            else:
                self.context_dict[self.instance.__class__.__name__.lower()] = self.instance
        return RequestContext(request, self.context_dict)
        
    def get_extra_context(self, request):
        """ Extend this method to add any additional items to the context """
        return {}
    
    def process_form(self, request):
        """ Returns a response or raises a redirect exception """
        
        _formClass = self.get_form_class()
        
        form = _formClass(**self.get_form_kwargs(request))
        
        if request.method == 'POST':
            if form.is_valid():
                self.save_form(form)
                self.context_dict[self.form_name] = form
                r = self.get_success_response(request)
                if r:
                    return r
            else:
                flashMessage.send("Please correct the errors below.", flashMessage.ERROR)
        
        self.context_dict[self.form_name] = form
        return None
        
    def save_form(self, form):
        """ Saves the form to a instance if available """
        if self.instance:
            self.instance = form.save()
        else:
            form.save()
        
    def get_form_class(self, *args, **kwargs):
        """ Here you can perform any changes to the form class """
        return self.formClass
        
    def get_success_response(self, request):
        """
            On successful submission of the form, redirect to the returned URL
            Returns None if redirect not necessary
        """
        if self.instance:
            return HttpResponseRedirect(self.instance.get_absolute_url())
        else:
            return None
        
    def get_form_kwargs(self, request):
        """ Get the parameters for the form class """
        import sys
        kwargs = {}
        if request.method == 'POST':
            kwargs['data'] = request.POST
            if self.has_upload and request.FILES:
                kwargs['files'] = request.FILES
        if self.instance:
            kwargs['instance'] = self.instance
        return kwargs
        
    def __str__(self):
        return "FormActionView"