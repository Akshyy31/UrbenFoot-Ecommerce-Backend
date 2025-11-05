import traceback
from django.http import JsonResponse

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Log the error in console or file
            print("Error:", e)
            traceback.print_exc()

            return JsonResponse(
                {"success": False, "message": "Internal Server Error", "error": str(e)},
                status=500
            )