from json import dumps

from apps.authentication.forms.auth import FormSignUp
from apps.authentication.models import GroupDetails
from apps.main.forms import FormGroupDetails, FormProfileEdit, FormUserEdit
from apps.services.apigateway import apigateway
from apps.services.apistar import apistar
from apps.services.decorators import group_required, login_required
from apps.services.utils import profilesync
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q, Value
from django.db.models.functions import Concat
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================

@login_required
@group_required('admin')
def table(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = True
    context['select2']          = True
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = False
    context['duallistbox']      = False
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False


    # ===[Fetch Data]===
    context['datagroup']        = Group.objects.all()


    # ===[Render Template]===
    return render(request, 'main/account/table.html', context)



@login_required
@group_required('admin')
def role(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = True
    context['select2']          = False
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = False
    context['duallistbox']      = False
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False


    # ===[Load Form]===
    context['datagroup']        = Group.objects.select_related('groupdetails')

    # ===[Render Template]===
    return render(request, 'main/account/role.html', context)



@login_required
@group_required('admin')
def edit_group(request, id):
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

    # ===[Check ID IsValid]===
    try:
        getgroupdetails = GroupDetails.objects.get(group_id=id)
    except GroupDetails.DoesNotExist:
        messages.error(request, 'Data Not Found!')
        return redirect('main:account_role')


    # ===[Load Form]===
    context['formgroupdetails']     = FormGroupDetails(request.POST or None, instance=getgroupdetails)


    # ===[Edit Logic]===
    if request.POST:
        if context['formgroupdetails'].is_valid():
            context['formgroupdetails'].save()

            messages.success(request, 'Data Edited Successfully', extra_tags=dumps({
                'redirect'      : reverse('main:account_role'),
                'confbtntxt'    : 'Check Data',
                'denybtntxt'    : 'Cancel',
            }))
            return redirect('main:account_edit_group', id=id)
        else:
            messages.error(request, context['formgroupdetails'].get_errors())


    # ===[Render Template]===
    return render(request, 'main/account/edit_group.html', context)



@login_required
@group_required('admin')
def add(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = False
    context['select2']          = True
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = True
    context['duallistbox']      = True
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False

    # ===[Load Form]===
    context['formsignup']       = FormSignUp(request.POST or None)
    context['formprofile']      = FormProfileEdit(request.POST or None, request.FILES or None)

    # ===[Fetch Data]===
    context['groups']           = Group.objects.all()

    # ===[Add Logic]===
    if request.POST:
        if context['formsignup'].is_valid():
            if context['formprofile'].is_valid():
                user = context['formsignup'].save()
                usergroups = request.POST.getlist('groups[]')
                user.groups.clear()
                user.groups.set(usergroups)
                user.save()

                profile = context['formprofile'].save(commit=False)
                profile.user = user
                profile.save()

                messages.success(request, 'Data Added Successfully', extra_tags=dumps({
                    'redirect'      : reverse('main:account_table'),
                    'confbtntxt'    : 'Check Data',
                    'denybtntxt'    : 'Cancel',
                }))
                return redirect('main:account_add')
            else:
                messages.error(request, context['formprofile'].get_errors())
        else:
            messages.error(request, context['formsignup'].get_errors())


    # ===[Render Template]===
    return render(request, 'main/account/add.html', context)



@login_required
@group_required('admin')
def generate(request):
    # ===[Check ID IsValid]===
    try:
        datakaryawan = apigateway.getKaryawan()
        for karyawan in datakaryawan['data']:
            # if not User.objects.filter(username=karyawan['uniid']).exists():
            print(karyawan['uniid'])
            user, is_success = profilesync(karyawan['uniid'])
    except Exception as e:
        messages.error(request, f'Terdapat kesalahan pada sistem. {str(e)}')
        return redirect('main:account_table')

    messages.success(request, 'Berhasil generate akun dari data kepegawaian.')
    return redirect('main:account_table')


@login_required
@group_required('admin')
def edit(request, id):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = False
    context['select2']          = True
    context['summernote']       = False
    context['maxlength']        = False
    context['inputmask']        = True
    context['duallistbox']      = True
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False


    # ===[Check ID IsValid]===
    try:
        user = User.objects.get(id=id)
        context['usergroups'] = user.groups.values_list('id',flat=True)
    except User.DoesNotExist:
        messages.error(request, 'Data Not Found!')
        return redirect('main:account_table')

    # ===[Load Form]===
    context['formsignup']       = FormUserEdit(request.POST or None, instance=user)
    context['formprofile']      = FormProfileEdit(request.POST or None, request.FILES or None, instance=user.profile)


    # ===[Fetch Data]===
    context['groups']           = Group.objects.all()


    # ===[Edit Logic]===
    if request.POST:

        if context['formsignup'].is_valid():
            if context['formprofile'].is_valid():
                user = context['formsignup'].save()
                profile = context['formprofile'].save(commit=False)
                profile.user = user
                profile.save()

                if request.POST.get('password1') and request.POST.get('password2'):
                    if request.POST.get('password1') != request.POST.get('password2'):
                        messages.error(request, 'Confirm password is not the same.')
                        return redirect('main:account_edit', id=id)

                    elif len(request.POST.get('password1')) < 8:
                        messages.error(request, 'Your password must contain at least 8 characters.')
                        return redirect('main:account_edit', id=id)

                    elif request.POST.get('password1').isnumeric():
                        messages.error(request, 'Your password cannot be entirely numeric.')
                        return redirect('main:account_edit', id=id)

                    else:
                        user.set_password(request.POST.get('password1'))
                        user.save()



                usergroups = request.POST.getlist('groups[]')
                user.groups.clear()
                user.groups.set(usergroups)


                messages.success(request, 'Data Updated Successfully', extra_tags=dumps({
                    'redirect'      : reverse('main:account_table'),
                    'confbtntxt'    : 'Check Data',
                    'denybtntxt'    : 'Cancel',
                }))
                return redirect('main:account_edit', id=id)

            else:
                messages.error(request, context['formprofile'].get_errors())
        else:
            messages.error(request, context['formsignup'].get_errors())

    # ===[Render Template]===
    return render(request, 'main/account/edit.html', context)



@login_required
@group_required('admin')
def import_user(request):
    context = {}
    # ===[Load a CSS And JS File]===
    context['datatables']       = True
    context['tinydatepicker']   = False
    context['datetimepicker']   = False
    context['select2']          = True
    context['chosen']           = False
    context['dropzone']         = False
    context['summernote']       = False
    context['fullcalendar']     = False
    context['photoswipe']       = False
    context['maxlength']        = False
    context['inputmask']        = False
    context['moment']           = False
    context['duallistbox']      = False
    context['daterange']        = False
    context['countdown']        = False


    # ===[Fetch Data]===
    context['datakaryawan']     = []
    context['showpopover']      = True


    if request.GET and request.GET.get('kepeg'):
        context['showpopover']  = False
        context['kepeg']        = request.GET.get('kepeg')

        if context['kepeg'] == 'all':
            getkaryawan = apigateway.getKaryawan()
        elif context['kepeg'] == 'dosen':
            getkaryawan = apigateway.getKaryawan('dosen')
        elif context['kepeg'] == 'tendik':
            getkaryawan = apigateway.getKaryawan('tendik')
        else:
            getkaryawan = {'status' : False, 'message' : 'Invalid request!'}

        if getkaryawan['status'] :
            context['datakaryawan']     = getkaryawan['data']
        else:
            messages.error(request, getkaryawan['message'])


    if request.POST and request.POST.getlist('list_id'):
        list_id = request.POST.getlist('list_id')
        try:
            with transaction.atomic():
                for uniid in list_id:
                    user, is_success = profilesync(uniid)
                messages.success(request, 'Data Imported Successfully')

        except User.DoesNotExist:
            messages.error(request, 'There is an error')



    # ===[Render Template]===
    return render(request, 'main/account/sync.html', context)




# =====================================================================================================
#                                                SERVICE
# =====================================================================================================

@login_required
@group_required('admin')
def deletelist(request):
    if request.POST and request.POST.getlist('list_id'):
        list_id = request.POST.getlist('list_id')

        with transaction.atomic():
            for id in list_id:
                try:
                    getuser = User.objects.get(id=id)
                    getuser.profile.image.delete()
                    getuser.delete()
                    messages.success(request, 'Data Deleted Successfully')

                except Exception as e:
                    transaction.set_rollback(True)
                    messages.error(request, 'There is an error')
                    break
    else:
        messages.error(request, 'Invalid request!')

    # ===[Redirect]===
    return redirect('main:account_table')



@login_required
@group_required('admin')
def delrole(request, userid, groupid):
    try:
        user = User.objects.get(id=userid)
        user.groups.remove(groupid)
        messages.success(request, 'Data Updated Successfully')
        return redirect('main:account_role')
    except User.DoesNotExist:
        messages.error(request, 'Data Not Found!')
        return redirect('main:account_role')



@login_required
@group_required('admin')
def setisactive(request, mode):
    if request.POST and request.POST.getlist('list_id'):
        list_id = request.POST.getlist('list_id')

        with transaction.atomic():
            for id in list_id:
                try:
                    getuser = User.objects.get(id=id)
                    if mode == 'active':
                        getuser.is_active = True
                    else:
                        getuser.is_active = False
                    getuser.save()
                    messages.success(request, 'Data Updated Successfully')

                except Exception as e:
                    transaction.set_rollback(True)
                    messages.error(request, 'There is an error')
                    break
    else:
        messages.error(request, 'Invalid request!')

    # ===[Redirect]===
    return redirect('main:account_table')



@login_required
@group_required('admin')
def synclist(request):
    if request.POST and request.POST.getlist('list_id'):
        list_id = request.POST.getlist('list_id')

        with transaction.atomic():
            for id in list_id:
                try:
                    user = User.objects.get(id=id)
                    user, is_success = profilesync(user)
                    if is_success:
                        messages.success(request, 'Profile sync successful')
                    else:
                        transaction.set_rollback(True)
                        messages.error(request, 'Failed to sync profile')
                        break

                except Exception as e:
                    transaction.set_rollback(True)
                    messages.error(request, 'There is an error')
                    break
    else:
        messages.error(request, 'Invalid request!')

    # ===[Redirect]===
    return redirect('main:account_table')



@login_required
@group_required('admin')
def datatable(request):
    queryset = User.objects.all().exclude(is_superuser=True)

    group_id = request.POST.get('group_id')
    if group_id and group_id != 'all':
        queryset = queryset.filter(groups__id=group_id)

    keyword = request.POST.get('search[value]', '')
    if keyword:
        queryset = queryset.annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(username__icontains=keyword) |
            Q(full_name__icontains=keyword)
        )

    queryset = queryset.order_by('id').distinct()

    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))

    if length > 0:
        paginator = Paginator(queryset, length)
        page_number = start // length + 1
        page_obj = paginator.get_page(page_number)
        records_filtered = paginator.count
    else:
        page_obj = queryset
        records_filtered = queryset.count()

    data = {
        'draw': int(request.POST.get('draw', 0)),
        'recordsTotal': queryset.count(),
        'recordsFiltered': records_filtered,
        'data': [
            {
                'id'            : data.id,
                'username'      : data.username,
                'email'         : data.email,
                'full_name'     : data.get_full_name(),
                'groups'        : list(data.groups.all().values_list('groupdetails__alias', flat=True)),
                'is_active'     : data.is_active,
                'image_url'     : data.profile.image_url(),
                'phone_number'  : data.profile.phone_number,
                'is_dosen'      : data.profile.get_jabfung(),
                'home_id'       : data.profile.home_id,
                'homebase'      : data.profile.homebase,
            }
            for data in page_obj
        ],
    }

    return JsonResponse(data)



@login_required
@group_required('admin')
def api_data_employee(request):
    getkaryawan = {'status' : False, 'message' : 'Invalid request!', 'data':[]}

    if request.POST and request.POST.get('kepeg'):
        kepeg = request.POST.get('kepeg')

        if kepeg == 'all':
            getkaryawan = apigateway.getKaryawan()
        elif kepeg == 'dosen':
            getkaryawan = apigateway.getKaryawan('dosen')
        elif kepeg == 'tendik':
            getkaryawan = apigateway.getKaryawan('tendik')

    return JsonResponse(getkaryawan)


@login_required
def by_lembaga_json(request):
    lembaga = request.GET.get('lembaga')

    qs = User.objects.select_related('profile')

    if lembaga != 'all':
        qs = qs.filter(profile__home_id=lembaga)

    data = [
        {
            "id": u.id,
            "text": f"{u.get_full_name()} | {u.username} | {u.profile.nip}"
        }
        for u in qs
    ]

    return JsonResponse(data, safe=False)
