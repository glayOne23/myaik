# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.db.models import F
from django.urls import reverse

from apps.services.apigateway import apigateway
from apps.services.apistar import apistar
from urllib.parse import urlencode





def setsession(request, user: User) -> User:
    # request.session.set_expiry(7200)
    request.session['user'] = {
        'username'      : user.username,
        'first_name'    : user.first_name,
        'last_name'     : user.last_name,
        'email'         : user.email,
        'is_superuser'  : user.is_superuser,
        'is_staff'      : user.is_staff,
        'date_joined'   : user.date_joined.strftime("%Y:%m:%d %H:%M:%S") if user.date_joined else user.date_joined,
        'last_login'    : user.last_login.strftime("%Y:%m:%d %H:%M:%S") if user.last_login else user.last_login,
        'image'         : user.profile.image_url(),
        'fullname'      : user.get_full_name() if user.get_full_name() else user.username,
        'groups'        : list(user.groups.annotate(alias=F('groupdetails__alias')).values('name','alias')),
    }


    if user.is_superuser:
        request.session['user']['groups'].insert(0, {'name': 'superuser', 'alias' : 'Super User'})

    return user





def split_full_name(full_name: str, max_len: int = 30):
    """
    Memisahkan full_name menjadi first_name dan last_name.
    Aturan:
    - first_name maksimal max_len karakter.
    - last_name = sisa kata, boleh > max_len.
    - Pemisahan tidak boleh di tengah kata.
    """

    # Normalisasi: hilangkan spasi ganda
    full_name = " ".join(full_name.strip().split())

    if not full_name:
        return "", ""

    words = full_name.split()
    first_name = ""
    last_name = ""

    for i, word in enumerate(words):
        # Jika kata masih bisa ditambahkan ke first_name
        if len(first_name) + len(word) + (1 if first_name else 0) <= max_len:
            first_name = f"{first_name} {word}".strip()
        else:
            # Sisanya langsung jadi last_name
            last_name = " ".join(words[i:])
            break

    return first_name, last_name





def profilesync(user) -> User:
    try:
        username = user.username
    except:
        username = user


    user, created   = User.objects.get_or_create(username = username)
    if created:
        print('Create a new user {}'.format(username))

    profile         = apigateway.getProfile(username) if settings.API_GATEWAY_USERNAME and settings.API_GATEWAY_PASSWORD else None
    is_success      = False # If successful in getting data from the API


    # check if he is an employee
    if profile and profile['status'] and profile['data'] :
        is_success = True

        if type(profile['data']) == list:
            data = profile['data'][0]
        else:
            data = profile['data']

        if 'nip' in data and data['nip']:
            user.profile.nip            = data['nip']

        if 'nidn' in data and data['nidn']:
            user.profile.nidn           = data['nidn']

        if 'surelluar' in data and data['surelluar']:
            user.profile.ext_email      = data['surelluar']

        if 'nomorhp' in data and data['nomorhp']:
            user.profile.phone_number   = data['nomorhp']

        if 'is_dosen' in data and data['is_dosen']:
            user.profile.is_dosen       = data['is_dosen']

        if 'home_id' in data and data['home_id']:
            user.profile.home_id        = data['home_id']

        if 'homebase' in data and data['homebase']:
            user.profile.homebase       = data['homebase']

        if 'fname' in data and data['fname']:
            user.first_name             = data['fname']

        if 'lname' in data and data['lname']:
            user.last_name              = data['lname']

        if 'nama_bergelar' in data and data['nama_bergelar']:
            first_name, last_name = split_full_name(full_name=data['nama_bergelar'], max_len=100)
            user.first_name = first_name
            user.last_name = last_name

        if username:
            user.email              = '{}@ums.ac.id'.format(str(username).lower())



    # otherwise it means he is a student
    else :
        is_success = False

        # use apistar to check if he is a student here
        if hasattr(settings,'API_STAR_URL') and hasattr(settings,'API_STAR_USERNAME') and hasattr(settings,'API_STAR_PASSWORD') and settings.API_STAR_URL and settings.API_STAR_USERNAME and settings.API_STAR_PASSWORD:
            getmhs = apistar.getMhsProfile(username)
            if getmhs and getmhs['success'] and str(getmhs['success']).lower() != 'false':
                is_success = True
            else:
                getmhs = False

        else:
            # ===[GET DATA MAHASISWA WITHOUT AUTH]===
            getmhs = apistar.getMhsProfileWithoutAuth(username)
            if getmhs and getmhs['success'] and str(getmhs['success']).lower() != 'false':
                is_success = True
            else:
                getmhs = False


        # If successful in getting student data from the API
        if getmhs:
            user.email = '{}@student.ums.ac.id'.format(str(username).lower())
            if 'Nama' in getmhs and getmhs['Nama']:
                first_name, last_name = split_full_name(full_name=getmhs['Nama'], max_len=100)
                user.first_name = first_name
                user.last_name = last_name

    user.save()
    user.profile.save()
    return user, is_success





def send_otp_by_email(request, user: User, viewname):
    user.profile.otp = get_random_string(16)
    user.save()

    staticurl   = request.build_absolute_uri(settings.STATIC_URL)
    otp_url     = request.build_absolute_uri(reverse(viewname))
    otp_params  = { 'email': user.email, 'otp': user.profile.otp }
    otp_url     += '?' + urlencode(otp_params)

    data = {
        'name'                      : user.get_full_name() if user.get_full_name() else user.username,
        'url'                       : otp_url,
        'staticurl'                 : staticurl,
        'APP_SHORT_NAME'            : settings.APP_SHORT_NAME,
        'APP_COMPANY_SHORT_NAME'    : settings.APP_COMPANY_SHORT_NAME,
        'APP_YEAR'                  : settings.APP_YEAR,
    }

    message = render_to_string('authentication/verify_email.html', data)

    return send_mail(
        subject         = 'Your email needs to be verified',
        message         = message,
        from_email      = settings.EMAIL_HOST_USER,
        recipient_list  = [user.email],
        fail_silently   = False,
        html_message    = message
    )





def username_in_cas(username:str) -> bool:
    '''
    Check if the username has been registered in the cas account
    return TRUE if the username is already registered in cas
    return FALSE if the username has not been registered with cas
    '''

    getuser = apigateway.getProfile(username)
    if getuser['status'] :
        return True
    else :
        if hasattr(settings,'API_STAR_URL') and hasattr(settings,'API_STAR_USERNAME') and hasattr(settings,'API_STAR_PASSWORD') and settings.API_STAR_URL and settings.API_STAR_USERNAME and settings.API_STAR_PASSWORD:
            getuser = apistar.getMhsProfile(username)
            if getuser and getuser['success'] and str(getuser['success']).lower() != 'false':
                return True
            else:
                return False

        else:
            getuser = apistar.getMhsProfileWithoutAuth(username)
            if getuser and getuser['success'] and str(getuser['success']).lower() != 'false':
                return True
            else:
                return False





def data_jabfung(uid=None):
    data = {
        1 : 'Dosen',
        2 : 'Administrasi Umum dan Akademik',
        3 : 'Laboran',
        4 : 'Pustakawan',
        5 : 'Programer',
        6 : 'Teknisi',
        7 : 'Administrasi Keuangan',
    }

    try:
        if uid:
            return data[uid]
        return data
    except:
        return None