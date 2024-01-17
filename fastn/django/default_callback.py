from django.contrib.auth import login
from django.contrib.auth.models import User

from fastn import utils


def callback(request, fastn_user: dict):
    first_name, last_name = utils.get_first_name_and_last_name(
        fastn_user.get("name", "")
    )

    user, _ = User.objects.get_or_create(
        username=fastn_user.get("username"),
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": fastn_user.get("email"),
        },
    )

    login(request, user)
