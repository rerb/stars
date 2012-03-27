from django.db import models
from django.utils.functional import curry
    
"""
So, I need a way to run something like this:

ETLObjectClass.objects.etl_run_update()

I create a manager that knows which source_class the
ETLObjectClass needs

I intend to do this by creating the manager using __new__
to curry the etl_run_udpate method with the ``etl_source_class``
from the model
"""

class ETLCompareMixin(object):
    """
        Allows a model to be comparable for changes since a previous sync
        
        models must define an ``etl_exclude_fields`` list property
        models must also define a "etl_source_class" property
        
        Note: using the "etl_" prefix for methods to avoid conflicts
    """
    
    @classmethod
    def etl_run_update(cls):
        """
            Runs an update of all the ETL objects for this class
            
            Takes the ``source_class`` to populate from
        """
        source_class = getattr(cls, 'etl_source_class')
        
        updates = []
        for obj in source_class.objects.all():
    
            # See if an ETL object exists for this source_class object
            try:
                old_etl = cls.objects.get(id=obj.id)
            except cls.DoesNotExist:
                old_etl = None
    
            # Create the new version
            new_etl = cls()
            new_etl.populate(obj)
    
            if not old_etl:
                # If there wasn't an old_etl, create it
                new_etl.save()
                updates.append(obj.id)
    
            elif old_etl.etl_update(new_etl):   
                # Otherwise, update as necessary 
                updates.append(obj.id)
    
        drops = []
        # remove any extraneous institutions in ETL
        for etl in cls.objects.all():
            try:
                i = source_class.objects.get(id=etl.id)
            except source_class.DoesNotExist:
                drops.append(etl.id)
                etl.delete()
    
        return (updates, drops)
            
    def etl_has_changed(self, obj):
        """
            Compares two ETL objects for equality. Compare everything except exclude_comparison_fields
            Returns True if equal and False if not
        """

        for field in self._meta.get_all_field_names():
            if field not in self.etl_exclude_fields:
                try:
                    if getattr(self, field) != getattr(obj, field):
                        return True
                except:
                    pass
        return False

    def etl_update(self, new_etl):
        """
            Compares one etl object to a new verison of itself

            return true if updated/created false if no change
        """

        if self.etl_has_changed(new_etl):
            self.delete()
            new_etl.save()
            # print "Updated ETL: %s" % new_etl
            return True
        return False
    
    def populate(self, obj):
        """
            Populate with the contents of another object to be mirrored
        """
        raise NotImplementedError
    
    def populate_all(self, obj):
        """
            Populate all the fields in this model with the fields from obj
            
            with the exception of self.etl_populate_exclude_fields
        """

        for field in self._meta.get_all_field_names():
            if field not in self.etl_populate_exclude_fields:
                setattr(self, field, getattr(obj, field))