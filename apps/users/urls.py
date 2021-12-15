
from django.urls import path, register_converter, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token

from apps.users.views import UsernameCountView, MobileCountView, RegisterView, RegisterCanteenView, UserAuthorizeView, \
    CanteenCountView, CanteenMobileCountView, CanteenUserAuthorizeView
from utils.myconverters import UsernameConverter, PhoneConverter

register_converter(UsernameConverter, 'user')
register_converter(PhoneConverter, 'phone')

urlpatterns = [
    # 学生端用户名验证
    path('stuusernames/<user:username>/count', UsernameCountView.as_view()),
    # 学生端手机号验证
    path('stustumobiles/<phone:mobile>/count', MobileCountView.as_view()),
    # 食堂端用户名验证
    path('canusernames/<user:username>/count', CanteenCountView.as_view()),
    # 食堂端手机号验证
    path('canmobiles/<phone:mobile>/count', CanteenMobileCountView.as_view()),
    # 注册用户
    path('register/', RegisterView.as_view()),
    # 注册食堂用户
    path('register/2/', RegisterCanteenView.as_view()),
    # 学生端登录验证 自定义类
    path('authorizations/', UserAuthorizeView.as_view()),
    # 食堂端登陆
    path('authorizations/2/', CanteenUserAuthorizeView.as_view()),
    # # 刷新token
    # path('refresh/', refresh_jwt_token),
    # # 用户个人信息
    # path('info/', UserInfoView.as_view()),
    # # 修改 密码
    # path('password/', UpdatePassword.as_view()),


]

router = DefaultRouter()
urlpatterns += router.urls



