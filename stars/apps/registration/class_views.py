from stars.apps.accounts.utils import respond

class RegistrationFormView(object):

    def __init__(self):
        pass
    
    def __call__(self, request):
        return self.main(request, extra_context={})

    def main(self, request, id, template_name=None, extra_context={}):
        #Logic
        obj = get_object_or_404(self.model, id=id)

        # Get Context
        context = self.get_context(request)
        apply_extra_context(extra_context, context)

        #Get Template
        template = self.get_template(request, template_name)

        #Render Template
        rendered_template = template.render(context)
        return HttpResponse(rendered_template) 

    def get_template(self, request, template_name): 
        """ 
        Returns the loaded Template
        """
        if not template_name:
            template_name = self.template
        return loader.get_template(template_name)

    def get_context(self, request, obj): 
        """ 
        Returns the Context
        """ 
        return RequestContext(request, {'object': obj})
