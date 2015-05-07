# PythonAuthenticationLib

A library for authenticating against the UserService

## Installation

	pip install tokenauth

## Usage 

Add to installed apps:

```
INSTALLED_APPS = (
    ...
    'tokenauth',
) 
```

Add to middleware:

```
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'tokenauth.middleware.TokenAuthMiddleware',
)
```

**Add authentication backends**

```
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'tokenauth.authbackends.TokenAuthBackend'
)
```

**Add userservice url**

	USERSERVICE_BASE_URL = "http://example.com"

**Profit**

$$

You can now authenticate against the UserService: 

	from django.contrib.auth.models import User
	user.authenticate(token)