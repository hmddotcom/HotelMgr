# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
description.

import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/Hotelerie'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'hotel_project.settings_production'

# Import and configure Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()