import hashlib

from django.shortcuts import render
import json, re
from datetime import datetime

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken

from apps.users.models import User, Canteen
from apps.users.serializers import CreateUserSerializer, CreateCanteenSerializer

"""
判断用户名是否重复
前端： 用户输入用户名， 失去焦点， 发送一个axios(ajax)请求
后端：
	接收请求，： 接收用户
	路由； get /usernames/<username>/count/
	业务逻辑：
		根据用户名，查询数据库， 查询当前数量， 数量大于0说明已经注册过了
	响应：json格式
		{"count":1, "code": "0", "errmsg": "ok"}

"""


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response({"count": count, 'code': "0", "errmag": "ok"})


"""
食堂名字查重

"""


class CanteenCountView(APIView):
    def get(self, request, username):
        count = Canteen.objects.filter(can_name=username).count()
        return Response({"count": count, 'code': "0", "errmag": "ok"})


"""
判断手机号是否重复注册
前端：用户输入手机号，失去焦点，发送一个axios（ajax）请求
后端：
    接受请求： 接收用户手机号
    路由： get mobiles/<phone:mobile>/count/
    业务逻辑：
        根据手机号，查询数据库，查询当前数量，数量大于0说明已经注册过了
    响应：json格式
        {"count":1,"code":"0", "errmsg": "ok"}
"""


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {"count": count, "code": "0", "errmsg": "ok"}
        return Response(data)


"""
食堂手机查询
"""


class CanteenMobileCountView(APIView):
    def get(self, request, mobile):
        count = Canteen.objects.filter(can_tel=mobile).count()
        data = {"count": count, "code": "0", "errmsg": "ok"}
        return Response(data)


"""
注册学生
前端： 用户输入 用户名，密码，确认密码，手机号，同意协议，点击注册按钮 发送axios 请求
后端：
    接受请求：  接受json 数据
    路由：  post  '/register/'
    业务逻辑： 验证数据，保存到数据库
    响应 json 格式
        {"code": "0", "errmsg": "ok"}
        {"code": "400", "errmsg": "register fail"}
"""


class RegisterView(CreateAPIView):
    serializer_class = CreateUserSerializer


"""
注册 食堂
前端： 用户输入食堂名，用户名， 密码，确认密码，手机号，身份证号，同意协议，点击注册按钮，发送zxios 请求
后端： 
    接受请求：   接收json
    路由： post  '/register/2/'
    业务逻辑： 验证数据，保存到数据库
    响应  json 格式
        {"code": "0", "errmsg": "ok"}
        {"code": "400", "errmsg": "register fail"}
"""


class RegisterCanteenView(CreateAPIView):
    serializer_class = CreateCanteenSerializer


"""
学生端登录
前端：     用户输入手机号， 密码， 短信验证码，

后端： 
    接收请求， Post 验证 手机号，密码，
    逻辑：
        从数据库取出，用户名，密码， 进行验证
    路由：
        post '/login/1/'
    
    响应：
        json格式
        {"code":"0","errmsg":"ok"}
        {"code":"400","errmsg":"fail"}


"""
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserAuthorizeView(ObtainJSONWebToken):
    """登录视图"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            print("序列化对象")
            print(serializer.object)
            print("serializer.object.get('token')")
            print(token)
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""
食堂端登录
前端：     用户输入手机号， 密码， 短信验证码，

后端： 
    接收请求， Post 验证 手机号，密码，
    逻辑：
        从数据库取出，用户名，密码， 进行验证
    路由：
        post '/login/1/'
    
    响应：
        json格式
        {"code":"0","errmsg":"ok"}
        {"code":"400","errmsg":"fail"}


"""


class CanteenUserAuthorizeView(APIView):
    """登录视图"""

    def post(self, request, *args, **kwargs):
        # print(request.user)
        # print(request.data)
        serializer_class = JSONWebTokenSerializer

        serializer = JSONWebTokenSerializer(data=request.data, *args, **kwargs)
        # print(serializer.token())
        if serializer.is_valid():
            print(serializer.object.get('token'))
            print("用户token11111")

        # #  获取用户名，密码
        # mobile = request.data.get("username")
        # pwd = request.data.get("password")
        #
        # # 数据库查询数据
        # try:
        #     user = Canteen.objects.get(can_tel=mobile)
        #     # print("用户的token",user.object.get('token'))
        #     # 进行密码判断
        #     md5 = hashlib.md5()
        #     md5.update(pwd.encode())
        #     if user.password == md5.hexdigest():
        #         return Response("200on 成功")
        # except Exception as e:
        #     print(e)
        #     return Response("400, 数据错误")
        #
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
