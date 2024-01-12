# fastn_py

Python package to facilitate working with [fastn](https://fastn.com/)

## Requirements

- **Python** 3.6 and above
- **Django** 4.0 and above

## Installation

```
pip install fastn
```

## GithubAuthMiddleware

- Add `'fastn.django.GithubAuthMiddleware'` to `MIDDLEWARE` after
  `django.contrib.auth.middleware.AuthenticationMiddleware`.

- By default, this middleware will create a [django
  User](https://docs.djangoproject.com/en/5.0/ref/contrib/auth/#user-model)
  from fastn session and call
  [`login()`](https://docs.djangoproject.com/en/5.0/topics/auth/default/#django.contrib.auth.login)
  on this user. To change this behaviour, add the following to your
  `settings.py` file:

    ```python
    FASTN_AUTH_CALLBACK = "some.module.auth_callback"
    ```

    the `some.module.auth_callback` will be called with
    [`request`](https://docs.djangoproject.com/en/5.0/ref/request-response/#httprequest-objects)
    and `fastn_user`. `fastn_user` is a dict:

    ```python
    fastn_user = {
        "username": "john", 
        "name": "John Do", 
        "email": "john@mail.com", 
    }
    ```
