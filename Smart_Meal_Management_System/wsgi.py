"""
WSGI config for Smart_Meal_Management_System project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application
from Smart_Meal_Management_System.settings import BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Meal_Management_System.settings')

from whitenoise import WhiteNoise

application = get_wsgi_application()
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles_build'))

app = application
