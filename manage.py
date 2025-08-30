#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    # Ensure the default settings module points to our development settings
    # so that `runserver` uses dev.py by default.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Helpful error message if Django isn't installed in the active venv
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?"
        ) from exc
    # Execute the management command passed on the command line (e.g., runserver, migrate)
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
