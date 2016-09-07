import os
import sys
import time
import traceback
import signal

current_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(current_directory)
module_name = os.path.basename(current_directory)

sys.path.append(parent_directory)
sys.path.append(current_directory)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
