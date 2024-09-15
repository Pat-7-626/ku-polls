"""middleware.py for Custom404Middleware."""

import logging
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class Custom404Middleware:
    """A class to go to index page when 404 occurred."""
    def __init__(self, get_response):
        """Get response."""
        self.get_response = get_response

    def __call__(self, request):
        """Go to index page when 404 occurred."""
        response = self.get_response(request)
        if response.status_code == 404:
            logger.error("404 error occurred for URL: %s", request.path)
            return HttpResponseRedirect(reverse('polls:index'))
        return response
