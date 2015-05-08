import requests
from django.conf import settings 
from django.contrib.auth.models import User

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.permissions import SAFE_METHODS
from django.utils import timezone


class UserSyncronizer(object):

    fields = ['id', 'first_name', 'last_name', 'username', 
              'email', 'is_staff', 'is_superuser']

    def fetch_user_from_service(self, token):

        headers = {
            'content-type': 'application/json', 
            'Authorization':'Token {0}' . format (token)
        }
        url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)
        return requests.get(url, headers=headers)

    def map_user_data(self, data):
        user_data = {}
        for field in self.fields: 
            value = data.get(field, None)
            if value is not None:
                user_data[field] = value

        return user_data


    def sync(self, data):
        
        user_data = self.map_user_data(data)
        try:
            user = User.objects.get(username=data.get("username", None))
            
            for key, value in user_data.items():
                print "set {0} to {1}" . format (key, value)
                setattr(user, key, value)

        except User.DoesNotExist:
            user = User(**user_data)

        if user.last_login is None:
            user.last_login = timezone.now()

        user.save()
        return user

class TokenAuthBackend(object):

    def __init__(self):
        self.syncer = UserSyncronizer()

    def authenticate(self, token):
        '''
        Will authenticate a user based on the token provided against the UserService
        '''        
        response = self.syncer.fetch_user_from_service(token)

        if response.status_code == 200:
            user = self.syncer.sync(response.json())
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class UserServiceAuthBackend(object):

    def __init__(self):
        self.syncer = UserSyncronizer()

    def authenticate(self, username, password):
        '''
        Will authenticate a user against the UserService
        '''

        url = '{0}/api-token-auth/' . format(settings.USERSERVICE_BASE_URL)
        response=requests.post(url, data={"username":username, "password":password})
        
        if response.status_code == 200:
            token = response.json().get("token")
            user_response = self.syncer.fetch_user_from_service(token)
            user = self.syncer.sync(user_response.json())
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
        #print "RESTTokenAuthBackend._get_token: {0}" . format(token)

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

        


