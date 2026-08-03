"""
ASGI config for sentiment_analysis_in_emergency_calls project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentiment_analysis_in_emergency_calls.settings')

application = get_asgi_application()
