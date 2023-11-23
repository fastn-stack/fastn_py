import logging
import os
import json

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin

from fastn.utils import AESCipher

logger = logging.getLogger(__name__)

SECRET_KEY = "FASTN_SECRET_KEY"
COOKIE_NAME = "github"


class GithubAuthMiddleware(MiddlewareMixin):
    """
    Add authenticated fastn user to django's authentication system
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def _add_user_or_redirect(self, request: HttpRequest):
        github_cookie = request.COOKIES.get(COOKIE_NAME)

        if github_cookie is None:
            if request.user.is_authenticated:
                logout(request)
            return

        key_str = os.environ.get(SECRET_KEY)

        if key_str is None:
            logger.warning(
                f"{SECRET_KEY} is required to use this middleware. Continuing anyway."
            )
            logger.warning(f"Use the same {SECRET_KEY} you used to configure fastn.")

        ci = AESCipher(key_str or "")

        try:
            # { username: String, name: String, access_token: String }
            fastn_user = json.loads(ci.decrypt(github_cookie))
        except json.decoder.JSONDecodeError:
            # failed to decode json
            return redirect_to_login(request.get_full_path())

        username = fastn_user["username"]
        name = fastn_user["name"].split(" ")
        first_name = name[0]
        last_name = ""

        if len(name) >= 2:
            last_name = name[1]

        user, _ = User.objects.get_or_create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email="",
            password="",
        )

        login(request, user)

    def process_request(self, request: HttpRequest):
        """
        Use process_request instead of defining __call__ directly;
        Django's middleware layer will process_request in a coroutine in __acall__ if it detects an async context.
        Otherwise, it will use __call__.
        https://github.com/django/django/blob/acde91745656a852a15db7611c08cabf93bb735b/django/utils/deprecation.py#L88-L148
        """
        return self._add_user_or_redirect(request)
