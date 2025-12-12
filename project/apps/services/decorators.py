# =========================================
# Created by Ridwan Renaldi, S.Kom. (rr867)
# =========================================
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache
from functools import wraps
import time



def group_required(*groups, signin_url='authentication:signin', signout_url='authentication:signout'):
    def decorator(function):
        @wraps(function)  # jaga metadata fungsi asli
        def wrapper(request, *args, **kwargs):
            user = request.user

            # Check authentication
            if not user.is_authenticated:
                messages.warning(request, 'Please login first.')
                return redirect(signin_url)

            # check groups by instance
            if user.groups.filter(name__in=groups).exists() or user.is_superuser:
                return function(request, *args, **kwargs)

            # check groups by session
            session_groups = request.session.get('user', {}).get('groups', [])
            if any(group.get('name') in groups for group in session_groups):
                return function(request, *args, **kwargs)

            messages.warning(request, 'You Don\'t Have Permission')
            return redirect(signout_url)

        return wrapper
    return decorator



def logout_required(redirect_url):
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return function(request, *args, **kwargs)
        return wrapper
    return decorator



def ajax_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponseBadRequest('Bad Request: AJAX request required.')
        return view_func(request, *args, **kwargs)
    return wrapper



def throttle_requests(rate=5, period=60):
    """
    Batasi max `rate` request dalam `period` detik per user/IP.

    Args:
        rate (int): Maksimum request yang diizinkan.
        period (int): Periode waktu dalam detik.

    Usage:
        @throttle_requests(rate=10, period=60)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                identifier = f"user-{request.user.id}"
            else:
                # ambil IP sederhana
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR', '')
                identifier = f"ip-{ip}"

            cache_key = f"throttle_{identifier}_{request.path}"
            now = time.time()

            request_times = cache.get(cache_key, [])
            # filter request yang masih dalam periode
            request_times = [t for t in request_times if now - t < period]

            if len(request_times) >= rate:
                return HttpResponse(
                    "Too many requests. Please try again later.",
                    status=429
                )

            request_times.append(now)
            cache.set(cache_key, request_times, timeout=period)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator