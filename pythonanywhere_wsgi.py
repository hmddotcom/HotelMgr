# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
description.

import os
import sys

# Add your project directory to the sys.path
path = '/home/netsama/HotelMgr'
if path not in sys.path:
    sys.path.append(path)

# Also add the parent directory for proper module resolution
parent_path = '/home/netsama'
if parent_path not in sys.path:
    sys.path.append(parent_path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'hotel_project.settings_production'

# Import and configure Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()