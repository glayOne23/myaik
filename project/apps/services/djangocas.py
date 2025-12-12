# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import update_last_login
from django.contrib.auth.models import User, Group
from django.urls import reverse

from django_cas_ng.backends import CASBackend
from django_cas_ng.views import LoginView


from apps.services.utils import profilesync, setsession


class CustomLoginView(LoginView):


    def successful_login(self, request: HttpRequest, next_page: str) -> HttpResponse:
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).


        :param request:
        :param next_page:
        :return:
        """
        try:
            user = User.objects.get(username=request.user.username)
        except User.DoesNotExist:
            user = request.user

        setsession(request, user)
          
        update_last_login(None, user)
        return HttpResponseRedirect(next_page)






class CustomCASBackend(CASBackend):
    def configure_user(self, user: User) -> User:
        """
        Configures a user after creation and returns the updated user.

        This method is called immediately after a new user is created,
        and can be used to perform custom setup actions.

        :param user: User object.

        :returns: [User] The user object. By default, returns the user unmodified.
        """

        user, is_success = profilesync(user)
        return user
