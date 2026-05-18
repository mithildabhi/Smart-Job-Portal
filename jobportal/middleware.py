from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Adds basic security response headers and optional CSP from env.

    - Sets X-Content-Type-Options
    - Sets Referrer-Policy
    - Optionally sets Content-Security-Policy if CSP_HEADER env var is set
    """
    def process_response(self, request, response):
        # Prevent MIME type sniffing
        response.setdefault('X-Content-Type-Options', 'nosniff')
        # Referrer policy
        response.setdefault('Referrer-Policy', getattr(settings, 'SECURE_REFERRER_POLICY', 'same-origin'))
        # Permissions policy (minimal)
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=()')
        # Optional CSP from env var to avoid breaking local dev
        csp = getattr(settings, 'CSP_HEADER', None)
        if csp:
            response.setdefault('Content-Security-Policy', csp)
        return response
