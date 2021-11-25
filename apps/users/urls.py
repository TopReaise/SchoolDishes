
from django.urls import path, register_converter, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token

urlpatterns = [
    # path('usernames/<user:username>/count', UsernameCountView.as_view()),

]

router = DefaultRouter()

urlpatterns += router.urls



