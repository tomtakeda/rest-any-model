def get_filter_property(field, operator):
    filter_property = field

    if operator != 'eq':
        filter_property += '__' + operator

    return filter_property
