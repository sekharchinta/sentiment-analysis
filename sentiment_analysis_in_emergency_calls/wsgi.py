"""
WSGI config for sentiment_analysis_in_emergency_calls project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentiment_analysis_in_emergency_calls.settings')

application = get_wsgi_application()
