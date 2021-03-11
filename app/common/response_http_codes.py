def response_http_codes(keys):
    codes = {
        200: {
            'description': 'Success'
        },
        201: {
            'description': 'Created'
        },
        204: {
            'description': 'Deleted'
        },
        400: {
            'description': 'Bad request'
        },
        404: {
            'description': 'Not found'
        },
        422: {
            'description': 'Unprocessable entity'
        },
        503: {
            'description': 'Database error'
        }
    }
    result = dict()
    for key in keys:
        if key in codes.keys():
            result.update({
                key: codes[key]
            })
    return result
