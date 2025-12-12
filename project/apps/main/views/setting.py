from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction

from apps.services.decorators import group_required, login_required
from apps.main.models import Setting
from apps.main.forms import FormSetting

from json import dumps





# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================

@login_required
@group_required('admin')
def edit(request):
    context = {}
    # ===[Select CSS and JS Files]===
    context['datatables']       = False
    context['select2']          = False
    context['summernote']       = True
    context['maxlength']        = False
    context['inputmask']        = False
    context['duallistbox']      = False
    context['moment']           = False
    context['daterange']        = False
    context['chartjs']          = False

    # ===[Check ID IsValid]===
    context['datasetting']      = Setting.objects.all()
    context['inputchar']        = Setting.getmode('char')
    context['inputtext']        = Setting.getmode('text')
    context['inputfile']        = Setting.getmode('file')



    # ===[Edit Logic]===
    if request.POST:
        for key, value in request.POST.items():
            if not value:
                value = request.POST.getlist(key)
                value = value[0]

            if key.isdigit():
                try:
                    getsetting = Setting.objects.get(id=key)
                    context['formsetting'] = FormSetting({ 'value' : value } or None, instance=getsetting)
                    
                    if context['formsetting'].is_valid():
                        context['formsetting'].save()
                    else:
                        messages.error(request, context['formsetting'].errors)
                        return redirect('main:setting_edit')
                except Exception as e:
                    print('[ERROR] : ', e)


        for key, value in request.FILES.items():
            if key.isdigit():
                try:
                    getfile = request.FILES.get(key)
                    getsetting = Setting.objects.get(id=key)

                    value = request.POST.getlist(key)[0] if request.POST.getlist(key) else None
                    context['formsetting'] = FormSetting(data={ 'value' : value }, files={'file' : getfile}, instance=getsetting)
                    if context['formsetting'].is_valid():
                        context['formsetting'].save()
                    else:
                        messages.error(request, context['formsetting'].errors)
                        return redirect('main:setting_edit')
                except Exception as e:
                    print('[ERROR] : ', e)

        messages.success(request, 'Data Edited Successfully')
        return redirect('main:setting_edit')



    # ===[Render Template]===
    return render(request, 'main/setting/edit.html', context)



# =====================================================================================================
#                                                SERVICE
# =====================================================================================================

@login_required
@group_required('admin')
def deletefile(request, id):
    try:
        getsetting = Setting.objects.get(id=id)
        getsetting.file.delete()
        messages.success(request, 'Data Deleted Successfully')
    except Setting.DoesNotExist:
        messages.error(request, 'Data Not Found!')

    return redirect('main:setting_edit')