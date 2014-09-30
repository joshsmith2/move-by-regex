__author__ = 'joshsmith'

from django.conf import settings
if not settings.configured:
    settings.configure(
        DATABASES={
            'default':{
                'ENGINE' : 'django.db.backends.sqlite3',
                'NAME' : 'mbr_db.db'
            }

        },
        INSTALLED_APPS=("move-by-regex")
    )


from models import *

