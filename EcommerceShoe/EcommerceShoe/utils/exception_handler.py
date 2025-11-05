from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        customized_response = {
            "success": False,
            "error": response.data,
            "message": "Something went wrong"
        }
        return Response(customized_response, status=response.status_code)
    
    # Handle unhandled exceptions
    return Response(
        {"success": False, "error": str(exc), "message": "Internal Server Error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
