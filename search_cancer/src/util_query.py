def add_limit(query, params, start, limit):
    '''
    Add start position and limit number to the query and params variable
    :param start: start position
    :param limit: limit number
    :return:
    '''
    if 'LIMIT' in query:
        raise ValueError("LIMIT exists in the query: " + query)
    if start > 0 and limit > 0:
        query += " LIMIT %s,%s"
        params += (start, limit,)
    elif limit > 0:
        query += " LIMIT %s"
        params += (limit,)
    elif start > 0:
        raise ValueError("start position or limit not provided: start: %s ; limit: %s" % start, limit)
    return query, params

