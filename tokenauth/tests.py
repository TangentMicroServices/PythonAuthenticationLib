from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from tokenauth.authbackends import TokenAuthBackend, UserServiceAuthBackend, UserSyncronizer
from tokenauth.test.mocks import mock_auth_success, mock_auth_failure

import requests 
import responses
import mock
from mock import patch

class UserSyncronizerTestCase(TestCase):
	
	def setUp(self):
		
		self.data = {
		  "id": 1,
		  "first_name": "Joe",
		  "last_name": "Soap",
		  "username": "joe.soap",
		  "email": "joe@soap.com",
		  "is_staff": True,
		  "is_superuser": True,
		  "profile": {
		    "contact_number": "",
		    "status_message": None,
		    "bio": None
		  },
		  "authentications": [],
		  "roles": []
		}

	def tearDown(self):
		for user in User.objects.all(): user.delete()

	def test_sync_new_user(self):

		syncer = UserSyncronizer()
		user = syncer.sync(self.data)

		new_user = User.objects.get(username="joe.soap")

		assert new_user.first_name == "Joe"
		assert new_user.last_name == "Soap"
		assert new_user.email == "joe@soap.com"
		assert new_user.is_staff == True
		assert new_user.is_superuser == True

	def test_sync_existing_user(self):

		data = {
			"id": 1, 
			"username": "joe.soap", 
			"first_name": "Peter",
			"last_name": "Pan",
			"is_staff": False,
			"is_superuser": False,
		}

		existing_user = User.objects.create(**data)

		syncer = UserSyncronizer()
		user = syncer.sync(self.data)

		assert user.first_name == "Joe"
		assert user.last_name == "Soap"
		assert user.email == "joe@soap.com"
		assert user.is_staff == True
		assert user.is_superuser == True

class UserServiceAuthBackendTestCase(TestCase):

	def tearDown(self):
		responses.reset()
		for user in User.objects.all(): user.delete()

	@responses.activate
	def test_authenticate_success(self):

		# initial assertions:
		assert User.objects.filter(id=1).count() == 0, 'Expect no users in local database'

		# setup:
		username = "joe"
		password = "test"

		# expected responses

		# login to userservice:
		url = '{0}/api-token-auth/' . format(settings.USERSERVICE_BASE_URL)
		response_string = '{"token": "123"}'
		responses.add(responses.POST, url,
              body=response_string, status=200,
              content_type='application/json')

		# get current user:
		url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)
		response_string = '{"id":1, "username":"joe.soap"}'
		responses.add(responses.GET, url,
              body=response_string, status=200,
              content_type='application/json')

		backend = UserServiceAuthBackend()
		user = backend.authenticate(username, password)

		# assert correct user is returned 
		assert user.id == 1
		assert user.username == 'joe.soap'

		# assert user is created
		assert User.objects.filter(id=1).count() == 1, 'Expect user to be created in local database'

	@responses.activate
	def test_autentication_failure(self):

		username = "joe"
		password = "test"

		# expected responses

		# login to userservice:
		url = '{0}/api-token-auth/' . format(settings.USERSERVICE_BASE_URL)
		response_string = '{"non_field_errors": ["Unable to login with provided credentials."]}'
		responses.add(responses.POST, url,
              body=response_string, status=400,
              content_type='application/json')

		backend = UserServiceAuthBackend()
		user = backend.authenticate(username, password)

		assert user is None, 'Expect authentication to fail'
		assert User.objects.filter(id=1).count() == 0, 'Expect no users in local database'

	## todo: work out why mocking isn't working here
	@responses.activate
	def test_userservice_is_called_if_user_not_in_local_db(self):
		'''
		If a user does not exist in the local DB, authenticate against UserService
		'''

		# login to userservice:
		url = '{0}/api-token-auth/' . format(settings.USERSERVICE_BASE_URL)
		response_string = '{"token": "123"}'
		responses.add(responses.POST, url,
              body=response_string, status=200,
              content_type='application/json')

		# get current user:
		url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)
		response_string = '{"id":1, "username":"joe.soap", "first_name": "From UserService"}'
		responses.add(responses.GET, url,
              body=response_string, status=200,
              content_type='application/json')
		
		user = authenticate(username='joe.soap', password='secret')

		assert user.username == 'joe.soap'
		assert user.first_name == 'From UserService'

	
	def test_userservice_is_not_called_if_user_is_in_local_db(self):
		'''
		If a user exists in the local DB, authenticate against local
		'''

		User.objects.create_user(username='joe.soap', password='secret', first_name='From local db')
		auth_user = authenticate(username='joe.soap', password='secret')

		assert auth_user.username == 'joe.soap'
		assert auth_user.first_name == 'From local db'


class TokenAuthBackendTestCase(TestCase):

	def tearDown(self):
		responses.reset()

	@responses.activate
	def test_authenticate(self):

		# setup:
		
		mock_auth_success()

		backend = TokenAuthBackend()
		
		token = 'some token'
		user = backend.authenticate(token)

		## assert that a user exists in the Users db
		django_user_created = User.objects.get(username='joe.soap')

		assert len(responses.calls) == 1, 'Expect only 1 call'
		assert user.username == "joe.soap", 'Expect the correct user to be returned'

	
	@responses.activate
	def test_authentication_fails(self):

		mock_auth_failure()

		backend = TokenAuthBackend()
		user = backend.authenticate("123")

		assert len(responses.calls) == 1, 'Expect only 1 call'
		assert user is None, 'Expect None to be returned if invalid user'		



from tokenauth.middleware import TokenAuthMiddleware

class TokenAuthMiddleWareTestCase(TestCase):

	def setUp(self):
		responses.reset()
		self.c = Client(Authorization='Token 123')

	@responses.activate
	def test_get_authenticates_a_valid_user(self):

		url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)		
		response_string = '{"username": "TEST"}'
		responses.add(responses.GET, url,
                  body=response_string, status=200,
                  content_type='application/json')

		response = self.c.get("/ping/")
		
		assert response.status_code == 200, 'Expect 200 OK'
		assert response.content == 'pong', 'Expect pong response'
		
		#assert response.user.username == 'TEST', 'Expect user is attached to response'

	@responses.activate
	def test_get_rejects_invalid_user(self):

		url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)		
		responses.add(responses.GET, url,
                  body='', status=401,
                  content_type='application/json')

		response = self.c.get("/ping/")

		assert response.status_code == 302, 'Expect a redirect to login page'

