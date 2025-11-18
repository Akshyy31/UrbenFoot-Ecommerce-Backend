import traceback
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)

        except (AuthenticationFailed, NotAuthenticated) as auth_error:
            # Return proper 401 authentication error
            return JsonResponse(
                {
                    "success": False,
                    "error": "Authentication failed",
                    "message": str(auth_error),
                },
                status=401,
            )

        except Exception as e:
            # Log the error and return 500 only for REAL server errors
            print("Error:", e)
            traceback.print_exc()

            return JsonResponse(
                {
                    "success": False,
                    "message": "Internal Server Error",
                    "error": str(e)
                },
                status=500
            )
