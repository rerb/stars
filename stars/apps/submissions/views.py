from stars.apps.credits.views import CreditsetStructureMixin
from stars.apps.submissions.models import SubmissionSet, CategorySubmission, SubcategorySubmission, CreditSubmission
from stars.apps.institutions.models import Institution

class SubmissionStructureMixin(CreditsetStructureMixin):
    """
        Extends the creditset structure to work with SubmissionSets
        
        URL structure can be one of the following
            /institution_slug/submissionset_date/category_abbreviation/subcategory_slug/credit_number/
            or
            /institution_slug/submissionset_id/category_abbreviation/subcategory_slug/credit_number/
    """
    
    def get_institution(self):
        """
            Attempts to get an institution.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        return self.get_obj_or_call(
                                    cache_key='institution',
                                    kwargs_key='institution_slug',
                                    klass=Institution,
                                    property="slug"
                                    )
    
    def get_submissionset(self):
        """
            Attempts to get a submissionset using the kwargs.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        
        if self.get_institution():
            kwargs_key = 'submissionset_id'
            property = 'pk'
            if self.kwargs.has_key('submissionset_date'):
                kwargs_key = 'submissionset_date'
                property = 'date_submitted'
                
            return self.get_obj_or_call(
                                        cache_key='submissionset',
                                        kwargs_key=kwargs_key,
                                        klass=self.get_institution().submissionset_set.all(),
                                        property=property
                                        )
            
    def get_creditset(self):
        """
            override get_creditset to extract from submissionset
        """
        if self.get_submissionset():
            return self.get_submissionset().creditset
        
    def get_categorysubmission(self):
        """
            Attempts to get a categorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_submissionset():
            return self.get_obj_or_call(
                                        cache_key='categorysubmission',
                                        kwargs_key="category_abbreviation",
                                        klass=self.get_submissionset().categorysubmission_set.all(),
                                        property='category__abbreviation'
                                        )
            
    def get_subcategorysubmission(self):
        """
            Attempts to get a subcategorysubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_categorysubmission():
            return self.get_obj_or_call(
                                        cache_key='subcategorysubmission',
                                        kwargs_key="subcategory_slug",
                                        klass=self.get_categorysubmission().subcategorysubmission_set.all(),
                                        property='subcategory__slug'
                                        )
            
    def get_creditusersubmission(self):
        """
            Attempts to get a creditusersubmission.
            Returns None if not in kwargs.
            Raises 404 if key in kwargs and not found.
        """
        if self.get_subcategorysubmission():
            return self.get_obj_or_call(
                                        cache_key='creditsubmission',
                                        kwargs_key="credit_number",
                                        klass=self.get_subcategorysubmission().creditusersubmission_set.all(),
                                        property='credit__number'
                                        )