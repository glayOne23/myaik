# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.conf import settings


def global_settings(request):
    # return any necessary values
    return {
        'APP_SHORT_NAME'        : settings.APP_SHORT_NAME,
        'APP_FULL_NAME'         : settings.APP_FULL_NAME,
        'APP_VERSION'           : settings.APP_VERSION,
        'APP_YEAR'              : settings.APP_YEAR,
        'APP_DEVELOPER'         : settings.APP_DEVELOPER,
        'APP_COMPANY_SHORT_NAME': settings.APP_COMPANY_SHORT_NAME,
        'APP_COMPANY_FULL_NAME' : settings.APP_COMPANY_FULL_NAME,
        'APP_LOGO'              : settings.APP_LOGO,
        'APP_FAVICON'           : settings.APP_FAVICON,
    }