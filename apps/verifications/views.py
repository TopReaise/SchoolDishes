from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from celery_tasks.sms.tasks import celery_send_sms_code

"""
图片验证码
前端：用户点击图片验证码， 生成uuid，拼接URL，发送请求
后端：
    请求 get 地址里的uuid
    路由  get '/image_codes/<uuid>/'
    业务逻辑： 接受uuid， 生成图片验证码， 保存到redis数据库
    响应  返回二进制数据
    

"""


class ImageCodeView(View):
    def get(self, request, uuid):
        # 1.获取uuid
        print(uuid)
        # 2. 生成验证码图片， 二进制数据
        text, image = captcha.generate_captcha()
        print(text)

        # 3.存到redis，uuid为key
        redis_cli = get_redis_connection('image_code')
        # uuid为key 120s是过期时间
        redis_cli.setex(uuid, 120, text)

        # 4.返回二进制图片数据
        return HttpResponse(image, content_type='image/jpeg')


"""
手机验证码
前端：  用户输入手机号， 点击获取短信验证码， 发送axiou 请求

后端：
    接受请求： 参数1 手机号， 2. 图片验证码， 3.uuid
    逻辑： 
        验证参数， 图片验证码，生成短信验证码，存入redis 数据库， 发送短信
    路由： 
        "sms_codes/<mobile>/?image_code=xxxx&image_code_id=xxxx"
    响应：
        {'code': 0, 'errmsg': "ok"}
"""


class MsmCodeView(View):
    def get(self, request, mobile):
        # 1. 获取参数
        mobile = mobile
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2. 验证参数， 是否存在
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmeg': '参数不全'})

        # 3. 图片验证码
        redis_cli = get_redis_connection("image_code")
        redis_image_code = redis_cli.get(uuid)

        # redis 删除图片
        try:
            redis_cli.delete(uuid)
        except Exception as e:
            print("删除图片uuid 错误")

        # 3.2 判断是否过有效期
        if redis_image_code is None:
            return JsonResponse({"code": 400, "errmsg": "图片验证码过期"})

        # 3.3 用户发过来的对比， redis_image_code 是二进制， 需要decode
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({"code": 400, "errmsg": "图片验证码过期"})

        # 4. 生成短信验证码
        # 0-999999
        from random import randint
        sms_code = "%06d" % randint(0, 999999)
        print("sms_code", sms_code)

        # 防止发送短信 过于频繁
        send_flag = redis_cli.get("send_flag_%s" % mobile)
        if send_flag:
            return JsonResponse({"code": 400, "errmsg": "短信发送过于频繁"})

        # 创建Redis 管道
        pl = redis_cli.pipeline()

        # 5 保存短信验证码到redis
        pl.setex("send_flag_%s" % mobile, 60, 1)
        pl.setex("sms_%s" % mobile, 300, sms_code)

        # 执行请求
        pl.execute()

        #  6. 发送短信  使用celery
        print('------->>>')
        # celery_send_sms_code.delay(mobile, sms_code)
        print('>>>>>异步')
        # 7 返回响应
        return JsonResponse({'code': 0, 'errmsg': "ok"})
