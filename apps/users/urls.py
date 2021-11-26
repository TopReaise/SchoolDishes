
from django.urls import path, register_converter, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token

from apps.users.views import UsernameCountView, MobileCountView, RegisterView
from utils.myconverters import UsernameConverter, PhoneConverter

register_converter(UsernameConverter, 'user')
register_converter(PhoneConverter, 'phone')

urlpatterns = [
    # 用户名验证
    path('usernames/<user:username>/count', UsernameCountView.as_view()),
    # 手机号验证
    path('mobiles/<phone:mobile>/count', MobileCountView.as_view()),
    # 注册用户
    path('register/', RegisterView.as_view()),

]

router = DefaultRouter()
urlpatterns += router.urls



