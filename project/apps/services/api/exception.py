from django.http import Http404
from django.core.exceptions import PermissionDenied

from rest_framework.serializers import as_serializer_error
from rest_framework.response import Response
from rest_framework import exceptions
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.views import exception_handler


class GenericAPIException(exceptions.APIException):
    """
    raises API exceptions with custom messages and custom status codes
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code != None:
            self.status_code = status_code


# def custom_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     if response != None:
#         response.data['status_code'] = response.status_code
#         response.data['message'] = response.data['detail']
#         del response.data['detail']
#     return response


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        if isinstance(exc, GenericAPIException):
            data = {
                "status_code":exc.status_code,
                "message": exc.message,
                "extra": exc.extra
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return response

    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    if isinstance(exc, exceptions.ValidationError):
        response.data['status_code'] = exc.status_code
        response.data["message"] = "Validation error"
        response.data["extra"] = {"fields": response.data["detail"]}
    else:
        response.data['status_code'] = exc.status_code
        response.data["message"] = response.data["detail"]
        response.data["extra"] = {}

    del response.data["detail"]

    return response