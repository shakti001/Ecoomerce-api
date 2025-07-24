# your_project/asgi.py

import os
from channels.routing import get_default_application
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

from ecomProject.routing import application as channels_app

application = channels_app
