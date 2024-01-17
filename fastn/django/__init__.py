import logging
import typing
import json

from django import forms
from django.conf import settings
from django.contrib.auth import logout
import django.http
from django.utils.deprecation import MiddlewareMixin
from django.utils import module_loading

import fastn.utils as utils

logger = logging.getLogger(__name__)
SECRET_KEY = getattr(settings, "FASTN_SECRET_KEY", getattr(settings, "SECRET_KEY", ""))
COOKIE_NAME = "fastn_session"
CI = utils.AESCipher(SECRET_KEY)
COOKIE_MAX_AGE = 365 * 24 * 60 * 60

FASTN_AUTH_CALLBACK = module_loading.import_string(
    getattr(settings, "FASTN_AUTH_CALLBACK", "fastn.django.default_callback.callback")
)


def action(form_class):
    def wrapper(request: RequestType):
        form = form_class(request)
        if not form.is_valid():
            return form.fastn_error_response()

        return form.save()

    return wrapper


class Form(forms.Form):
    def __init__(self, request):
        self.request = request
        data = json.loads(request.body.decode("utf-8"))
        super(Form, self).__init__(data)

    def fastn_error_response(self):
        return django.http.JsonResponse({"errors": self.errors})


def redirect(location):
    return django.http.JsonResponse(
        {
            "redirect": location,
        }
    )


def reload():
    return django.http.JsonResponse(
        {
            "reload": True,
        }
    )


class RequestType:
    def __init__(self):
        self.user: typing.Optional[django.contrib.auth.models.User] = None
        self.GET = django.http.QueryDict(mutable=True)
        self.POST = django.http.QueryDict(mutable=True)
        self.COOKIES = {}
        self.META = {}
        self.FILES = django.utils.datastructures.MultiValueDict()

        self.path = ""
        self.path_info = ""
        self.method = None
        self.resolver_match = None
        self.content_type = None
        self.content_params = None


class GithubAuthMiddleware(MiddlewareMixin):
    """
    Add authenticated fastn user to django's authentication system
    """

    def __init__(self, get_response):
        super(GithubAuthMiddleware, self).__init__(get_response)
        self.is_github_cookie_valid = True
        # One-time configuration and initialization.

    def _add_user(self, request: RequestType):
        fastn_auth_cookie = request.COOKIES.get(COOKIE_NAME)

        if fastn_auth_cookie is None:
            # end user session if they have logged out of fastn
            if request.user.is_authenticated:
                logout(request)
            return

        fastn_user = None

        try:
            # {'session_id': int, 'user': {'username': str, 'name': str, 'email': str, }}
            fastn_user = json.loads(CI.decrypt(fastn_auth_cookie)).get("user")
        except:
            self.is_github_cookie_valid = False
            logger.warning(
                "Failed to decrypt user from cookie. Wrong SECRET_KEY provided"
            )

        if fastn_user is None:
            return

        FASTN_AUTH_CALLBACK(request, fastn_user)

    def process_request(self, request: RequestType):
        """
        Use process_request instead of defining __call__ directly;
        Django's middleware layer will process_request in a coroutine in __acall__ if it detects an async context.
        Otherwise, it will use __call__.
        https://github.com/django/django/blob/acde91745656a852a15db7611c08cabf93bb735b/django/utils/deprecation.py#L88-L148
        """
        return self._add_user(request)


class DisableCSRFOnDebug(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request: RequestType):
        if settings.DEBUG:
            setattr(request, "_dont_enforce_csrf_checks", True)
