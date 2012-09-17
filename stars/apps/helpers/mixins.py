from django.contrib import messages

class StarsFormMixin(object):
    """
        A custom mixin to add a message upon success
    """
    valid_message = "Changes Saved Successfully"
    invalid_message = "Please correct the errors below"

    def get_valid_message(self):
        return self.valid_message

    def get_invalid_message(self):
        return self.invalid_message

    def form_valid(self, form):
        messages.success(self.request, self.get_valid_message())
        return super(StarsFormMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.get_invalid_message())
        return super(StarsFormMixin, self).form_invalid(form)
