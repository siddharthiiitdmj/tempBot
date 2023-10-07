from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import jwt

def auth_user(func):
    @wraps(func)
    def wrapper(self,request,*args, **kwargs):
        token=request.headers.get("token",None)
        if not token:
            return Response({'error':"Forbidden"},
                            status=status.HTTP_403_FORBIDDEN)
        
        try:
            jwt.decode(token, "secret",algorithms="HS256")
        except:
            return Response({'error':"Forbidden"},
                            status=status.HTTP_403_FORBIDDEN)
        
        return func(self,request,*args, **kwargs)
    
    return wrapper