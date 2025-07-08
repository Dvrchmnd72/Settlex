import os
import sys

# ✅ Add your project directory to the sys.path
project_home = "/home/Settlex/Settlex"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ✅ Ensure correct Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Settlex.settings")

# ✅ Activate Virtual Environment (if needed)
activate_env = "/home/Settlex/.virtualenvs/settlex-env/bin/activate_this.py"
if os.path.exists(activate_env):
    exec(open(activate_env).read(), dict(__file__=activate_env))

# ✅ Load the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
