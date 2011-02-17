class FormListWrapper(object):
    """
        A wrapper to make multiple forms appear as a single form
        to the generic django mixins
    """
    
    def __init__(self, form_dict):
        """
            Forms are stored in a list of dicts:
                {'context_name': form,}
        """
    
        self.forms = form_dict
        
    def save(self, commit=True):
        """
            Call the save method on all the forms in self.form_list
        """
        for k, form in self.forms.items():
            form.save(commit)
            
    def is_valid(self):
        """
            Run the is_valid method on all forms
            Return false if any fail
        """
        
        for k, form in self.forms.items():
            if not form.is_valid():
                return False
            
        return True