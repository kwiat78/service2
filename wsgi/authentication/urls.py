from django.conf.urls import url
from wsgi.authentication.views import AuthView
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # url(r'^login$', AuthView.as_view(), name='auth-login'),
    url(r'^login$', obtain_jwt_token),

]
