from django.core import serializers
import requests, responses, unittest, json
from django.conf import settings

def mock_get_me(user):
	url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)		
	
	users_json = serializers.serialize('json', [user])
	user_data = json.loads(users_json)[0]

	response = json.dumps(user_data.get("fields"))	
	return response
           
def mock_auth_success(user=None):

	url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)	
	if user is None:	
		response_string = '{"id": 1,"first_name": "Joe","last_name": "Soap","username": "joe.soap","email": "joe@tangentsolutions.co.za","is_staff": true,"is_superuser": true,"profile": {"contact_number": "","status_message": null,"bio": null},"authentications": [],"roles": []}'
	else:
		response_string = mock_get_me(user)

	responses.add(responses.GET, url,
              body=response_string, status=200,
              content_type='application/json')

def mock_auth_failure():

	url = '{0}/api/v1/users/me/' . format(settings.USERSERVICE_BASE_URL)		
	responses.add(responses.GET, url,
              body='', status=401,
              content_type='application/json')