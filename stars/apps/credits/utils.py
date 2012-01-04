def get_mappings():
    """
    Return a list of var names for mapping ints to variable names
    """

    var_names = []
    for i in range(0, 26):
        var_names.append(chr(i+65))
    
    for i in range(0, 3):
        for j in range(0, 26):
            var_names.append("%s%s" % (chr(i+65), chr(j+65)))

    return var_names

def int_to_var(num):
    """
    converts a number to a unique variable name
    """
    mappings = get_mappings()
    
    return mappings[num]

def var_to_int(var):
    """
    converts a variable name to a unique number
    """

    mappings = get_mappings()
    return mappings.index(var)

def get_next_variable_name(variable_list):
    """
    Takes a list of variable names and returns a new unique one.

    Variables are structured as so:
    A > B > B > ... > Z > AA > AB > ... > AZ > BA > BB > BC
    """

    v = 'A'
    if not variable_list:
        return v

    # convert all vars in list to numeric form
    num_list = []
    for v in variable_list:
        num_list.append(var_to_int(v))

    # get the highest number in the list and add one
    num_list.sort()
    next_num = num_list[-1] + 1

    # convert to variable name
    return int_to_var(next_num)

def migrate_set(old_cs, new_version_name, release_date):
    """ Copy a creditset to a new version and update `previous_version` references' """    
        
    def migrate_obj(old_obj, prop_dict, previous=True):
        
        new_obj = copy.copy(old_obj)
        new_obj.id = None
        if previous:
            new_obj.previous_version = old_obj
        for k,v in prop_dict.items():
            setattr(new_obj, k, v)
        new_obj.save()
        return new_obj
    
    new_cs = migrate_obj(old_cs, {'version': new_version_name, 'release_date': release_date})
    
    # ratings
    for r in old_cs.rating_set.all():
        new_r = migrate_obj(r, {'creditset': new_cs,})
        
    # categories, subcategories, credits, applicability reasons, documentation field, choice
    for cat in old_cs.category_set.all():
        new_cat = migrate_obj(cat, {'creditset': new_cs,})
        
        for sub in cat.subcategory_set.all():
            new_sub = migrate_obj(sub, {'category': new_cat,})
            
            for credit in sub.credit_set.all():
                new_c = migrate_obj(credit, {'subcategory': new_sub,})
                
                for ar in credit.applicabilityreason_set.all():
                    new_ar = migrate_obj(ar, {'credit': new_c,})
                    
                for field in credit.documentationfield_set.order_by('-id'):
                    new_f = migrate_obj(field, {'credit': new_c,})
                    
                    for choice in field.choice_set.all():
                        new_choice = migrate_obj(choice, {'documentation_field': new_f,})
                
                for cts in CreditTestSubmission.objects.filter(credit=credit):
                    new_cts = CreditTestSubmission(credit=new_c, expected_value=cts.expected_value)
                    new_cts.save()

                    for dfs in cts.get_submission_fields():
                        new_field = dfs.documentation_field.next_version
                        new_dfs = DocumentationFieldSubmission.get_field_class(dfs.documentation_field)(value=dfs.value, documentation_field=dfs.documentation_field.next_version, credit_submission=new_cts)
                        new_dfs.save()
    return new_cs
