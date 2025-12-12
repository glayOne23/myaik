from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction

from apps.services.decorators import group_required, login_required
from apps.main.models import Category
from apps.main.forms import FormCategory

from json import dumps





# =====================================================================================================
#                                               LOAD PAGE
# =====================================================================================================

@login_required
@group_required('admin')
def table(request):
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

    # ===[Fetch Data]===
    context['datacategory']     = Category.objects.all()

    # ===[Render Template]===
    return render(request, 'main/category/table.html', context)



@login_required
@group_required('admin')
def add(request):
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

    # ===[Load Form]===
    context['formcategory']     = FormCategory(request.POST or None, request.FILES or None)


    # ===[Insert Logic]===
    if request.POST:
        if context['formcategory'].is_valid():
            context['formcategory'].save()
            messages.success(request, 'Data Added Successfully', extra_tags=dumps({
                'redirect'      : reverse('main:category_table'), 
                'confbtntxt'    : 'Check Data',
                'denybtntxt'    : 'Cancel',
            }))
            return redirect('main:category_add')
        else:
            messages.error(request, context['formcategory'].get_errors())
    
    
    # ===[Render Template]===
    return render(request, 'main/category/add.html', context)



@login_required
@group_required('admin')
def edit(request, id):
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
        getcategory = Category.objects.get(id=id)
    except Category.DoesNotExist:
        messages.error(request, 'Data Not Found!')
        return redirect('main:category_table')


    # ===[Load Form]===
    context['formcategory']     = FormCategory(request.POST or None, request.FILES or None, instance=getcategory)


    # ===[Edit Logic]===
    if request.POST:
        if context['formcategory'].is_valid():
            context['formcategory'].save()

            messages.success(request, 'Data Edited Successfully', extra_tags=dumps({
                'redirect'      : reverse('main:category_table'), 
                'confbtntxt'    : 'Check Data',
                'denybtntxt'    : 'Cancel',
            }))
            return redirect('main:category_edit', id=id)
        else:
            messages.error(request, context['formcategory'].get_errors())


    # ===[Render Template]===
    return render(request, 'main/category/edit.html', context)





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
                    Category.objects.get(id=id).delete()
                    messages.success(request, 'Data Deleted Successfully')

                except Exception as e:
                    transaction.set_rollback(True)
                    messages.error(request, 'There is an error')
                    break
    else:
        messages.error(request, 'Invalid request!')

    # ===[Redirect]===
    return redirect('main:category_table')