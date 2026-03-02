from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages

from apps.services.utils import profilesync, setsession
from apps.services.decorators import group_required, login_required


@login_required
def setprofilesync(request):
    if request.POST:
        user, is_success = profilesync(request.user)
        if is_success:
            setsession(request, user)
            messages.success(request, 'Profile sync successful')
        else:
            messages.error(request, 'Failed to sync profile')
    else:
        messages.error(request, 'Invalid request!')

    # ===[Redirect]===
    return redirect(request.META.get('HTTP_REFERER', 'main:dashboard'))

