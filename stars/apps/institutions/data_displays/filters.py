"""
    Filter objects are used to filter data in the Data Displays
    They do their own work, to keep the logic out of the views
    
        - Manage URL GET Phrases
        - Generate Querysets for instances
        - Provide a title for the active filter
        - Get a list of choices
"""

class Filter(object):
    """
        Filters need to be a managed more programatically
        added and removed from the general list where avaialable
        
        Note: the `key` should be unique to the list of filters
        you are using
    """
    def __init__(self, key, title, item_list, base_qs):
        self.key = key
        self.title = title
        self.item_list = item_list
        self.base_qs = base_qs
        
    def delete_from_get(self, get_dict, selected_item):
        """
            Takes a GET QueryDict and removes the parameters for this
            form from that QueryDict
        """
        
    def get_active_title(self, item):
        " A name to display for this filter when active. "
        
        # Translation from form
        if item == "True":
            item = True
        elif item == "False":
            item = False
        
        if self.key == "rating__name":
            return "%s Rated Institutions" % item
        
        for k,v in self.item_list:
            if item == v:
                return k
            
        return item
        
    def get_select_list(self):
        """
            This is used to build the pull-down lists and 
            always returns a list of tuples despite the
            internal structure of item_list
        """
        return self.item_list
        
    def get_results(self, item):
        " Returns a queryset with the applied filter for item. "
        
        if item != 'DO_NOT_FILTER':
        # convert True and False from text
            if item == "True":
                item = True
            elif item == "False":
                item = False
            
            kwargs = {self.key: item,}
            
            return self.base_qs.filter(**kwargs)
            
        return self.base_qs

class RangeFilter(Filter):
    """
        Like a filter, but the item_list adds a min and max:
        
        Example:
        
        item_list = [
                ('Title', 'key', min, max),
                ('Under 5,000', 'u5000', 0, 5000 ),
                ('5,000-10,000', 5000-10000', 5000, 10000 ),
                ('Over 10,000', 'o10000', 10000, None ), # None exlcudes the upper bound
           ],
    """
    
    def get_active_title(self, item):
        " A name to display for this filter when active. "
        
        for i in self.item_list:
            if i[1] == item:
                return i[0]
    
    def get_select_list(self):
        """
            
        """
        select_list = []
        for i in self.item_list:
            select_list.append((i[0], i[1]))
        return select_list
        
    def get_results(self, item):
        " Returns a queryset with the applied filter for item (key). "

        for i in self.item_list:
            if i[1] == item:
                qs = self.base_qs
                if i[2]:
                    min_kwargs = {"%s__gte" % self.key: i[2]}
                    qs = self.base_qs.filter(**min_kwargs)
                if i[3]:
                    max_kwargs = {"%s__lt" % self.key: i[3]}
                    qs = self.base_qs.filter(**max_kwargs)
                return qs
        
        return None