# apps/accounts/middleware.py
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

class AxesRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, HttpResponseForbidden):
            return redirect('apps.accounts:blocked')
        return response