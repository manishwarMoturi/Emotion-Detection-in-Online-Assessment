from django.http import HttpResponseRedirect
from django.urls import reverse
import re

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile regex patterns for protected URLs
        self.dashboard_pattern = re.compile(r'.*-dashboard\.html$')
        self.profile_pattern = re.compile(r'.*-profile\.html$')
        self.results_pattern = re.compile(r'.*-results\.html$')
        self.exams_pattern = re.compile(r'.*-exams\.html$')
        # Updated pattern to exclude detect-emotion API as well
        self.api_pattern = re.compile(r'^/api/(?!login|register|check-mongodb|detect-emotion).*$')

    def __call__(self, request):
        # Skip for the login page, registration, or MongoDB check
        if request.path == '/' or request.path == '/api/login/' or request.path == '/api/register/' or request.path == '/api/check-mongodb/' or request.path == '/api/detect-emotion/':
            return self.get_response(request)

        # Check if user is trying to access a protected page
        is_dashboard = self.dashboard_pattern.match(request.path)
        is_profile = self.profile_pattern.match(request.path)
        is_results = self.results_pattern.match(request.path)
        is_exams = self.exams_pattern.match(request.path)
        is_protected_api = self.api_pattern.match(request.path)

        if (is_dashboard or is_profile or is_results or is_exams or is_protected_api) and not request.user.is_authenticated:
            # For API requests, return JSON response
            if request.path.startswith('/api/'):
                from django.http import JsonResponse
                return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
            
            # Redirect to login page
            return HttpResponseRedirect('/')

        # Role-based access control
        if request.user.is_authenticated:
            # Check if admin pages are accessed by admin users
            is_admin_page = 'admin-' in request.path
            if is_admin_page and not (request.user.role == 'admin' or request.user.is_superuser):
                if request.path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'error', 'message': 'Admin privileges required'}, status=403)
                return HttpResponseRedirect('/')
                
            # Check if testtaker pages are accessed by testtakers or admins
            is_testtaker_page = 'testtaker-' in request.path
            if is_testtaker_page and not (request.user.role == 'testtaker' or request.user.role == 'admin' or request.user.is_superuser):
                if request.path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'error', 'message': 'Testtaker privileges required'}, status=403)
                return HttpResponseRedirect('/')

        response = self.get_response(request)
        return response 