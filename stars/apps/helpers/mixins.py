from django.contrib import messages

class StarsFormMixin(object):
    """
        A custom mixin to add a message upon success
    """
    def get_valid_message(self):
        return "Changes Saved Successfully"
    
    def get_invalid_message(self):
        return "Please correct the errors below"
    
    def form_valid(self, form):
        messages.success(self.request, self.get_valid_message())
        return super(StarsFormMixin, self).form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, self.get_invalid_message())
        return super(StarsFormMixin, self).form_invalid(form)