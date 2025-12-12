from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User

from apps.services.utils import setsession
from apps.main.forms import FormMyProfile, FormChangePassword, FormChangePasswordNew
from apps.services.decorators import group_required, login_required





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
    
    # ===[Fetch Data]===
    context['datauser']         = request.user

    # ===[Load Form]===
    context['formprofile']      = FormMyProfile(request.POST or None, request.FILES or None, instance=request.user.profile)

    
    if request.user.password:
        # if the user already has a password
        context['formpassword']     = FormChangePassword(request.user, request.POST or None)
    else:
        # if the user doesn't have a password yet
        context['formpassword']     = FormChangePasswordNew(request.POST or None, instance=request.user)


    if request.POST:

        form = request.POST.get('form')
        if form in ['profile','password'] :
            
            # Change profile
            if form == 'profile':
                oldimage = request.user.profile.image
                
                if context['formprofile'].is_valid():
                    formprofile = context['formprofile'].save()
                    newimage = formprofile.image

                    if oldimage and oldimage.name != newimage.name and oldimage.storage.exists(oldimage.name) and not request.POST.get('_setprofile_'):
                        oldimage.delete(save=False)

                    if request.POST.get('_setprofile_') and oldimage and oldimage.storage.exists(oldimage.name):
                        oldimage.delete(save=False)
                        if newimage and newimage.storage.exists(newimage.name):
                            newimage.delete(save=False)
                        formprofile.image = ''
                        formprofile.save()
                    
                    request.user.refresh_from_db()
                    setsession(request, request.user)
                    messages.success(request, 'Data has been saved')
                else:
                    messages.error(request, context['formprofile'].get_errors())


            # Change password
            else:          
                if context['formpassword'].is_valid():
                    # ===[If there is already a password]===
                    if request.user.password:
                        user = context['formpassword'].save()
                        update_session_auth_hash(request, user)
                        messages.success(request, 'Your password was successfully updated!')

                    # ===[if you log in using "cas" then there is no password]===
                    else:
                        if request.POST.get('password1') != request.POST.get('password2'):
                            messages.error(request, 'Confirm password is not the same.')
                        
                        elif len(request.POST.get('password1')) < 8:
                            messages.error(request, 'Your password must contain at least 8 characters.')

                        elif request.POST.get('password1').isnumeric():
                            messages.error(request, 'Your password cannot be entirely numeric.')
                        
                        else:
                            getuser = User.objects.get(username=request.user.username)
                            getuser.set_password(request.POST.get('password1'))
                            getuser.save()
                            messages.success(request, 'Your password was successfully updated!')

                else:
                    messages.error(request, context['formpassword'].get_errors())

        else:
            messages.success(request, 'There is an error')

        return redirect('main:profile')
        
    # ===[Render Template]===
    return render(request, 'main/profile.html', context)
