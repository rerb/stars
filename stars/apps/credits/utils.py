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