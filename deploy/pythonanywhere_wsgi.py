import os
import sys
from pathlib import Path

from dotenv import load_dotenv


USERNAME = 'yourusername'
PROJECT_ROOT = Path(f'/home/{USERNAME}/Product/backend')

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
