from django.conf import settings

from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    if exception_class == 'ValidationError':
        response.data = {
            "success": False,
            "data": [],
            "errors": exc.__dict__['detail'],
        }

    if response is not None:
        response.data['statusCode'] = response.status_code

        if "success" not in response.data.keys():

            rsp_data = {
                "success": False,
                "statusCode": response.data['statusCode']
            }

            if "error" in response.data.keys():
                rsp_data['error'] = response.data.get("error")
            else:
                rsp_data['error'] = response.data.get("detail")

            response.data = rsp_data

    return response
