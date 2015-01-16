from django.contrib.auth import authenticate, login

class TokenAuthMiddleware(object):  
    def process_request(self, request):  

        token = request.META.get('Authorization', None)

        if not token is None:
        	token = token.replace("Token ", "")
	        user = authenticate(token=token)
	        
	        if user is not None:
	            if user.is_active:
	                login(request, user)
	                
        return None               
            
