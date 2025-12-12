from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse

from apps.services.decorators import group_required, login_required
from json import dumps





# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================
@login_required
def index(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = False
    context['select2']          = False
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = False
    context['duallistbox']      = False
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False


    # Example Notification
    # extra_tags is optional, used in the notif function located in -> (apps\main\templates\main\layout\javascript.html)

    # messages.success(request, 'Welcome to Dashboard', extra_tags=dumps({
    #     'redirect'      : reverse('main:dashboard'), 
    #     'confbtntxt'    : 'Check Data',
    #     'denybtntxt'    : 'Cancel',
    #     'title'         : 'Welcome',
    # }))


    # ===[Render Template]===
    return render(request, 'main/index.html', context)
