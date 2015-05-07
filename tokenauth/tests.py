from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User

from tokenauth.authbackends import TokenAuthBackend
from tokenauth.test.mocks import mock_auth_success, mock_auth_failure

import requests 
import responses
import mock

class TokenAuthBackendTestCase(TestCase):

	def setup(self):
		pass

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
	def test_authenticate_creates_new_user(self):

		# setup:		
		mock_auth_success()

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

