from apps.main.views import (account, category, dashboard, jabatan, lembaga,
                             pertemuan, presensi, profile, services, setting,
                             tipe_pertemuan)
from django.contrib.auth.decorators import login_required
from django.urls import include, path

app_name = 'main'

urlpatterns = [
    path('dashboard/',                              dashboard.index,            name='dashboard'),
    path('profile/',                                profile.index,              name='profile'),

    path('services/', include([
        path('setprofilesync/',                     services.setprofilesync,    name='services_setprofilesync'),
    ])),

    path('account/', include([
        # =================================================[ LOAD PAGE ]=================================================
        path('table/',                              account.table,              name='account_table'),
        path('role/',                               account.role,               name='account_role'),
        path('add/',                                account.add,                name='account_add'),
        path('generate/',                           account.generate,           name='account_generate'),
        path('edit/<int:id>/',                      account.edit,               name='account_edit'),
        path('edit_group/<int:id>/',                account.edit_group,         name='account_edit_group'),

        # ==================================================[ SERVICE ]==================================================
        path('delrole/<int:userid>/<int:groupid>/', account.delrole,            name='account_delrole'),
        path('deletelist/',                         account.deletelist,         name='account_deletelist'),
        path('synclist/',                           account.synclist,           name='account_synclist'),
        path('setisactive/<str:mode>/',             account.setisactive,        name='account_setisactive'),
        path('datatable/',                          account.datatable,          name='account_datatable'),
        path('import/',                             account.import_user,        name='account_import'),
        path('data_employee/',                      account.api_data_employee,  name='account_data_employee'),
    ])),


    path('category/', include([
        # =================================================[ LOAD PAGE ]=================================================
        path('table/',                              category.table,             name='category_table'),
        path('add/',                                category.add,               name='category_add'),
        path('edit/<int:id>/',                      category.edit,              name='category_edit'),

        # ==================================================[ SERVICE ]==================================================
        path('deletelist/',                         category.deletelist,        name='category_deletelist'),
    ])),

    path('setting/', include([
        # =================================================[ LOAD PAGE ]=================================================
        path('edit/',                               setting.edit,               name='setting_edit'),

        # ==================================================[ SERVICE ]==================================================
        path('deletefile/<int:id>/',                setting.deletefile,         name='setting_deletefile'),
    ])),

    path('admin/', include([
        path('lembaga/', include([
            # =================================================[ LOAD PAGE ]=================================================
            path('table/', lembaga.AdminLembagaListView.as_view(), name='admin.lembaga.table'),
            path('generate/', lembaga.AdminLembagaGenerateView.as_view(), name='admin.lembaga.generate'),
        ])),

        path('jabatan/', include([
            # =================================================[ LOAD PAGE ]=================================================
            path('table/', jabatan.AdminJabatanListView.as_view(), name='admin.jabatan.table'),
            path('generate/', jabatan.AdminJabatanGenerateView.as_view(), name='admin.jabatan.generate'),
        ])),

        path('tipe_pertemuan/', include([
            # =================================================[ LOAD PAGE ]=================================================
            path('table/', tipe_pertemuan.AdminTipePertemuanListView.as_view(), name='admin.tipe_pertemuan.table'),
            path('add/', tipe_pertemuan.AdminTipePertemuanCreateView.as_view(), name='admin.tipe_pertemuan.add'),
            path('<int:id>/update/', tipe_pertemuan.AdminTipePertemuanUpdateView.as_view(), name='admin.tipe_pertemuan.update'),
            # ==================================================[ SERVICE ]==================================================
            path('deletelist/', tipe_pertemuan.AdminTipePertemuanDeleteListView.as_view(), name='admin.tipe_pertemuan.deletelist'),
        ])),
        path('pertemuan/', include([
            # =================================================[ LOAD PAGE ]=================================================
            path('table/', pertemuan.AdminPertemuanListView.as_view(), name='admin.pertemuan.table'),
            path('add/', pertemuan.AdminPertemuanCreateView.as_view(), name='admin.pertemuan.add'),
            path('<int:id>/update/', pertemuan.AdminPertemuanUpdateView.as_view(), name='admin.pertemuan.update'),
            path('<int:pertemuan_id>/presensi/table/', presensi.AdminPresensiListView.as_view(), name='admin.presensi.table'),
            # ==================================================[ SERVICE ]==================================================
            path('deletelist/', pertemuan.AdminPertemuanDeleteListView.as_view(), name='admin.pertemuan.deletelist'),
        ])),
        path('presensi/', include([
            path('excel_import/', presensi.AdminPresensiExcelImportV2View.as_view(), name='admin.presensi.excel_import'),
            # =================================================[ LOAD PAGE ]=================================================
        ])),
    ])),

    path('user/', include([
        path('pertemuan/', include([
            # =================================================[ LOAD PAGE ]=================================================
            path('table/', pertemuan.UserPertemuanListView.as_view(), name='user.pertemuan.table'),
            path('<int:id>/presensi/add/', presensi.UserPresensiCreateView.as_view(), name='user.presensi.add'),
            # ==================================================[ SERVICE ]==================================================
            path('table_json/', pertemuan.UserPertemuanListJsonView.as_view(), name='user.pertemuan.table_json'),
        ])),

        path('presensi/', include([
            path('bagan/', presensi.UserPresensiBaganView.as_view(), name='user.presensi.bagan'),
            path('<int:presensi_id>/sertifikat/', presensi.UserPresensiSertifikatView.as_view(), name='user.presensi.sertifikat'),
            # =================================================[ LOAD PAGE ]=================================================
        ])),
    ])),
]
