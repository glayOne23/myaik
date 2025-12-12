# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.contrib.auth.models import User
from hijack import signals

from apps.services.utils import setsession


def print_hijack_started(sender, hijacker, hijacked, request, **kwargs):
    print('[Hijack] : {0} has hijacked {1}'.format(hijacker, hijacked))

    try:
        user = User.objects.get(username=hijacked)
        setsession(request, user)
    except User.DoesNotExist:
        print('[Error] : User not found')
    except Exception as e:
        print(e)

signals.hijack_started.connect(print_hijack_started)



def print_hijack_ended(sender, hijacker, hijacked, request, **kwargs):
    print('[Hijack] : {0} has released {1}'.format(hijacker, hijacked))

    try:
        user = User.objects.get(username=hijacker)
        setsession(request, user)
    except User.DoesNotExist:
        print('[Error] : User not found')
    except Exception as e:
        print(e)

signals.hijack_ended.connect(print_hijack_ended)
