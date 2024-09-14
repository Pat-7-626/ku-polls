"""apps.py for the poll app."""

from django.apps import AppConfig


class PollsConfig(AppConfig):
    """Polls app config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
