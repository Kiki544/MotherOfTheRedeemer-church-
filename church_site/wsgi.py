import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings
import dotenv 
dotenv.load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'church_site.settings')

# Only run migrations in production (when DEBUG=False)
if not settings.DEBUG:
    import django
    django.setup()
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])

application = get_wsgi_application()