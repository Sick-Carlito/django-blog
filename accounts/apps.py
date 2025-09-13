# accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # Import signals module to register signal handlers.
        # Import here to avoid AppRegistryNotReady errors at import time.
        try:
            import accounts.signals  # noqa: F401
        except Exception:
            # Avoid crashing manage commands if signals import fails during early setup.
            pass
