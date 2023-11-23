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

