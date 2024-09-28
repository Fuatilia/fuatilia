import logging
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger("app_logger")


def process_error_response(
    e: Exception,
) -> Response:
    logger.exception(e)

    if e.__class__ == IntegrityError:
        response_status = status.HTTP_409_CONFLICT
        error_str = e.__str__()

    elif e.__class__ == ObjectDoesNotExist:
        response_status = (status.HTTP_404_NOT_FOUND,)
        error_str = e.__str__()

    else:
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_str = e.__str__()

    return Response(data={"error": error_str}, status=response_status)
