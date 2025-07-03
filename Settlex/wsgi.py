import os
from django.core.wsgi import get_wsgi_application

# Set the correct settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Settlex.settings")  # 🔹 Update if necessary

# Load the WSGI application
application = get_wsgi_application()
