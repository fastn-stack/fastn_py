import logging
import os
import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from fastn.utils import AESCipher

logger = logging.getLogger(__name__)

SECRET_KEY = getattr(settings, "FASTN_SECRET_KEY", "FASTN_SECRET_KEY")
COOKIE_NAME = "github"


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
            if request.user.is_authenticated:
                logout(request)
            return

        key_str = os.environ.get(SECRET_KEY)

        if key_str is None:
            logger.warning(
                f"{SECRET_KEY} is required to use this middleware. Continuing with empty value. Remember to set {SECRET_KEY} in production!"
            )
            logger.warning(f"Use the same {SECRET_KEY} you used to configure fastn.")

        ci = AESCipher(key_str or "")

        # {'access_token': str, 'user': {'login': str, 'id': int, 'name': str | None, ' email': str | None}}
        fastn_user = json.loads(ci.decrypt(github_cookie)).get("user")

        if fastn_user is None:
            return

        name = fastn_user.get("name", "").split(" ")
        first_name = name[0]
        last_name = ""

        if len(name) >= 2:
            last_name = name[1]

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
