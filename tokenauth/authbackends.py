import requests
from django.conf import settings 
from django.contrib.auth.models import User

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.permissions import SAFE_METHODS

class TokenAuthBackend(object):

    def _fetch_user(self, token):

        headers = {
            'content-type': 'application/json', 
            'Authorization':'Token {0}' . format (token)
        }
        url = '{0}/users/me/' . format(settings.USERSERVICE_BASE_URL)
        return requests.get(url, headers=headers)

    def authenticate(self, token):
        '''
        Will authenticate a user based on the token provided against the UserService
        '''
        print "authenticate: {0}" . format(token)
        response = self._fetch_user(token)

        if response.status_code == 200:
            username = response.json().get("username", False)
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; 
                user = User(username=username, password='not important')
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class RESTTokenAuthBackend(authentication.BaseAuthentication):
    
    def _get_token(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        print "RESTTokenAuthBackend._get_token: {0}" . format(token)

        if not token is None:
            token = token.replace("Token ", "")
        return token

    def authenticate(self, request):
        
        token = self._get_token(request)
        backend = TokenAuthBackend()
        user = backend.authenticate(token)
        
        if user is None:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)

        


