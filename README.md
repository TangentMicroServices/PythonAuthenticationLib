# PythonAuthenticationLib

A library for authenticating against the UserService

## Installation

	pip install tangent-tokenauth

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

    ## this will allow you to authenticate against the userservice with a token
    'tokenauth.authbackends.TokenAuthBackend'
    ## this will allow you to authenticate against the userservice with a username and password
    'tokenauth.authbackends.UserServiceAuthBackend'
)
```

**Notes:** It is advisable to include `UserServiceAuthBackend` after `ModelBackend`. 
Since `UserServiceAuthBackend` will sync the user returned from the UserService, it will be preferable to login using the local synced user rather than hitting the UserService each time. 
From the frontend this will be transparent. 

**Add userservice url**

	USERSERVICE_BASE_URL = "http://example.com"

**Profit**

	$$

You can now authenticate against the UserService: 

	from django.contrib.auth.models import User

	# TokenAuthBackend
	user.authenticate(token)

	# UserServiceAuthBackend
	user.authenticate(username, password)
