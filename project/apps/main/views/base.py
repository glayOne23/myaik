from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.http import HttpResponseForbidden


# =====================================================================================================
#                                               MIXINS
# =====================================================================================================
def in_grup(user, grup_name):
    if user:
        return user.groups.filter(name=grup_name).count() > 0
    return False


class AdminRequiredMixin(AccessMixin):
    """Mixin untuk membatasi akses hanya untuk grup admin."""
    def dispatch(self, request, *args, **kwargs):
        if not in_grup(request.user, 'admin'):
            return HttpResponseForbidden("Anda tidak memiliki hak akses.")
        return super().dispatch(request, *args, **kwargs)


class CustomTemplateBaseMixin(LoginRequiredMixin):
    """Mixin dasar untuk semua view"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        return context