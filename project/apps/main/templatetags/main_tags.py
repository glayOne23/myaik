from django import template
from django.urls import reverse, NoReverseMatch
from django.conf import settings
from django.contrib.auth.models import User

register = template.Library()


# ==============================================================================================
#                                         AUTHORIZATION 
# ==============================================================================================

@register.filter('has_group')
def has_group(request, groups_name):
    group_list = [arg.strip() for arg in groups_name.split(',')]
    session_groups = [group['name'] for group in request.session.get('user', {}).get('groups', [])]

    if request.user.groups.filter(name__in=group_list).exists() or request.user.is_superuser: # check by instance
        return True
    elif any(group in group_list for group in session_groups): # check by session
        return True
    return False






# ==============================================================================================
#                                       CONTROL SIDEBAR
# ==============================================================================================
@register.simple_tag
def setactive(req, url, *args, css='', **kwargs):
    """
    url bisa berupa:
        - URL name: 'main:admin:buku_table'
        - URL path langsung: '/main/admin/buku/table/'
    """

    if not req:
        return ''
    
    current_path = req.path.rstrip('/') + '/'

    if isinstance(url, str) and url.startswith('/'):
        target_url = url.rstrip('/') + '/'

    else:
        try:
            target_url = reverse(url, args=args, kwargs=kwargs)
            target_url = target_url.rstrip('/') + '/'
        except NoReverseMatch:
            return ''

    if current_path.lower().startswith(target_url.lower()):
        return css

    return ''





# ==============================================================================================
#                                      DATA MANIPULATION
# ==============================================================================================
@register.filter(name='split')
def split(path, key):
    return path.split(key)


@register.filter(name='use_apigateway')
def use_apigateway(request):
    return True if settings.API_GATEWAY_USERNAME and settings.API_GATEWAY_PASSWORD else False