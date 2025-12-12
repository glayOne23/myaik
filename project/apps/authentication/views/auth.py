from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User

from apps.authentication.forms.auth import FormSignUp, FormSignUpProfile, FormSignIn, FormResetPassword
from apps.services.decorators import logout_required
from apps.services.utils import setsession, send_otp_by_email, username_in_cas




# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================

@logout_required('main:dashboard')
def signin(request):
    context = {}
    context['formsignin'] = FormSignIn(request, data=request.POST or None)
    context['email_config_available'] = ( hasattr(settings, 'EMAIL_HOST_USER') and hasattr(settings, 'EMAIL_HOST_PASSWORD') and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD )

    if request.POST:
        if context['formsignin'].is_valid():
            username = context['formsignin'].cleaned_data.get('username')
            password = context['formsignin'].cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:

                    setsession(request, user)
                    login(request, user)
                    messages.success(request, 'Sign in Success')

                    next = request.GET.get('next', 'main:dashboard')
                    return redirect(next)
                else:
                    messages.warning(request, 'This account is inactive. Please check your email for account verification or contact admin!')
                    # return redirect('authentication:signin')
            else:
                messages.warning(request, 'Please check your credentials and try again.')
                # return redirect('authentication:signin')
        else:            
            if '__all__' in context['formsignin'].errors.get_json_data():                
                messages.error(request, context['formsignin'].errors.get_json_data()['__all__'][0]['message'])
            else:
                messages.error(request, context['formsignin'].get_errors())            
    

    return render(request, 'authentication/signin.html', context)



@logout_required('main:dashboard')
def signup(request):
    context = {}
    context['formsignup']       = FormSignUp(request.POST or None)
    context['formsignupprofile']= FormSignUpProfile(request.POST or None)

    if request.POST:
        if context['formsignup'].is_valid():
            if context['formsignupprofile'].is_valid():

                if User.objects.filter(email=request.POST.get('email')).exists():
                    messages.error(request, 'Email has been used')
                    return redirect('authentication:signup')
                
                if username_in_cas(request.POST.get('username')):
                    messages.warning(request, 'The username has been registered in the cas system, please log in using cas')
                    return redirect('authentication:signup')
                
                user = context['formsignup'].save(commit=False)
                user.is_active = False
                user.save()

                context['formsignupprofile'] = FormSignUpProfile(request.POST or None, instance=user.profile)
                context['formsignupprofile'].save()

                if hasattr(settings,'EMAIL_HOST_USER') and hasattr(settings,'EMAIL_HOST_PASSWORD') and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                    # ===[SEND EMAIL VERIFICATION]===
                    try:
                        send_otp_by_email(request, user, 'authentication:verify')
                        messages.success(request, 'Please confirm your email address to complete the registration')
                        return redirect('authentication:signin')
                    except Exception as e :
                        print('[ERROR] : ', e)
                        messages.error(request, 'Failed to send notification to email. Please contact Admin or IT Support')
                        return redirect('authentication:signup')
                else:
                    messages.success(request, 'Congratulations, your account has been successfully created.')
                    return redirect('authentication:signin')
                
            else:
                messages.error(request, context['formsignupprofile'].get_errors())
        else:
            messages.error(request, context['formsignup'].get_errors())

    return render(request, 'authentication/signup.html', context)



@logout_required('main:dashboard')
def forgot(request):
    if request.POST:
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Please enter your email.')
            return redirect('authentication:forgot')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email not found. Please check again.')
            return redirect('authentication:forgot')

        try:
            send_otp_by_email(request, user, 'authentication:reset_password')
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('authentication:forgot')
        except Exception as e:
            print('[ERROR] : ', e)
            messages.error(request, 'Failed to send notification to email. Please contact Admin or IT Support')
            return redirect('authentication:forgot')

    context = {}
    return render(request, 'authentication/forgot.html', context)



def reset_password(request):
    context = {}
    context['email']    = request.GET.get('email', '')
    context['otp']      = request.GET.get('otp', '')
    context['formresetpassword'] = FormResetPassword(request.POST or None, request.FILES or None)


    if request.POST:
        if context['formresetpassword'].is_valid():
            context['formresetpassword'].save()
            messages.success(request, 'Your password has been reset. Please log in.')
            return redirect('authentication:signin')
        else:
            messages.error(request, context['formresetpassword'].get_errors())


    return render(request, 'authentication/reset_password.html', context)



# =====================================================================================================
#                                                SERVICE
# =====================================================================================================

def signout(request):
    logout(request)
    
    storage = messages.get_messages(request)
    if storage:
        for message in storage:
            messages.warning(request, message)
    else:
        messages.success(request, 'Success Signout')

    return redirect('authentication:signin')



def verify(request):
    if request.GET:
        if request.GET.get('email') and request.GET.get('otp'):
            try:
                user = User.objects.get(email=request.GET.get('email'), profile__otp=request.GET.get('otp'))
                user.is_active = True
                user.profile.otp = None
                user.save()
                messages.success(request, 'Your email address is successfully verified! Please login to access your account!')
            except User.DoesNotExist:
                messages.warning(request, 'Your email address failed to verify!')
        else:
            messages.warning(request, "Link doesn't match")
    else:
        messages.warning(request, 'Please check your email for account verification!')


    return redirect('authentication:signin')