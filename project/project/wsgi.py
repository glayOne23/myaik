"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os, sys, time

from django.core.wsgi import get_wsgi_application
from .settings import DATABASES, APP_SHORT_NAME

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()




def typewriter(say, message_speed = 0.02, new_line_delay_time = 0.5):
    for character in say:
        sys.stdout.write(character)
        sys.stdout.flush()
        
        if character != "\n":
            time.sleep(message_speed)
        else:
            time.sleep(new_line_delay_time)


space = round((50 - len(APP_SHORT_NAME)) / 2) * ' '
print("""
# ==================================================
# {}{}
# ==================================================
""".format(space, APP_SHORT_NAME))

db = DATABASES['default']
txt = '=====================[DATABASE]=====================\n'
txt += '• ENGINE \t: {}\n'.format(str(db['ENGINE']))
txt += '• NAME \t\t: {}\n'.format(str(db['NAME']))
txt += '• USER \t\t: {}\n'.format(str(db['USER']))
txt += '• PASSWORD \t: {}\n'.format(len(str(db['PASSWORD'])) * '*')
txt += '• HOST \t\t: {}\n'.format(str(db['HOST']))
txt += '• PORT \t\t: {}\n'.format(str(db['PORT']))
txt += '====================================================\n'

print(txt)
typewriter("Start Application...\n")







