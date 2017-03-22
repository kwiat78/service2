from django.contrib.auth import authenticate

import jwt

from rest_framework.response import Response
from rest_framework.views import APIView

from wsgi.authentication.serializers import LoginSerializer


class AuthView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        token = jwt.encode({'user': user.username}, 'secret', algorithm='HS256').decode()
        if user:
            return Response({'token': token}, status=200)
        else:
            return Response(status=401)
