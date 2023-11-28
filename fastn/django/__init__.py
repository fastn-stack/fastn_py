import logging
import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

import fastn.utils as utils

logger = logging.getLogger(__name__)

SECRET_KEY = getattr(settings, "FASTN_SECRET_KEY", getattr(settings, "SECRET_KEY", ""))

COOKIE_NAME = "github"

CI = utils.AESCipher(SECRET_KEY)


class GithubAuthMiddleware(MiddlewareMixin):
    """
    Add authenticated fastn user to django's authentication system
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def _add_user(self, request: HttpRequest):
        github_cookie = request.COOKIES.get(COOKIE_NAME)

        if github_cookie is None:
            # if request.user.is_authenticated:
            #     logout(request)
            return

        fastn_user = None

        try:
            # {'access_token': str, 'user': {'login': str, 'id': int, 'name': str | None, ' email': str | None}}
            fastn_user = json.loads(CI.decrypt(github_cookie)).get("user")
        except:
            logger.warning(
                "Failed to decrypt user from cookie. Wrong SECRET_KEY provided"
            )

        if fastn_user is None:
            return

        first_name, last_name = utils.get_first_name_and_last_name(
            fastn_user.get("name", "")
        )

        user, _ = User.objects.get_or_create(
            username=fastn_user.get("login"),
            first_name=first_name,
            last_name=last_name,
            email=fastn_user.get("email", ""),  # email has Not Null constraint
        )

        login(request, user)

    def process_request(self, request: HttpRequest):
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

    def process_request(self, request):
        if settings.DEBUG:
            setattr(request, '_dont_enforce_csrf_checks', True)
