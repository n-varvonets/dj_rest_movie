"""
WSGI config for django_movie project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_movie.settings')

application = get_wsgi_application()

# CREATE USER nick WITH PASSWORD 'QQQqqq111';
# CREATE DATABASE db_dj_rest_movie;
# GRANT ALL PRIVILEGES ON DATABASE db_dj_rest_movie to nick;
