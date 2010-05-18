import sys

from stars.apps.helpers.forms.views import TemplateView


# class CreditBrowsingView(TemplateView):
#     """
#         Class-based view that can
# 
#             - extract the Category, Subcategory, and Credit
#               from the variables passed to __call__()
# 
#             - provide the outline for the left nav menu for the CreditSet
# 
#         Thoughts:
# 
#             - use a `get_context_from_request` method so that it can be used with mixins
#     """
#     
#     def get_context(self, request, *args, **kwargs):
#         """ Expects arguments for category_id/subcategory_id/credit_id """
#         _context = get_submission_context(request, *args, **kwargs)
#         return _context
#         
#     def get_submission_context(self, request, *args, **kwargs):
#         """
#             Gets all the available contexts associated with a submission from the args
#         """
#         print >> sys.stderr, args