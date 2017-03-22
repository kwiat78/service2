from rest_framework.serializers import Serializer, CharField


class LoginSerializer(Serializer):
    username = CharField(required=False, allow_blank=True)
    password = CharField(style={'input_type': 'password'})


