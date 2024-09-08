import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in

logger = logging.getLogger('polls')


def log_user_login(sender, request, user, **kwargs):
    """Log user login with IP address."""
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged in from {ip_addr}")


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LogUserLoginMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        """Process request middleware"""
        if request.user.is_authenticated:
            user_logged_in.connect(log_user_login)
