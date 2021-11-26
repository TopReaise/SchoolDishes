from django.shortcuts import render
import json,re
from datetime import datetime

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers import CreateUserSerializer

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
        return Response({"count": count,'code': "0", "errmag": "ok"})



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
        data = {"count":count,"code":"0", "errmsg": "ok"}
        return Response(data)





"""
注册
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









