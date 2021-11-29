from rest_framework import serializers
import re
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from apps.users.models import User, School, Canteen


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    sch_name = serializers.CharField(label='学校名称', write_only=True)
    user_type = serializers.CharField(label='用户类型', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = User  # 从User模型类中映射序列化器字段
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token', 'sch_name','user_type']
        extra_kwargs = {  # 修改字段选项
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {  # 自定义 校验出错后的错误信息提示
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名'
                }

            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {  # 自定义 校验出错后的错误信息提示
                    'min_length': '仅允许5-20个字符的密码',
                    'max_length': '仅允许5-20个字符的密码'
                }
            }
        }

    def validate_mobile(self, value):
        """单独校验手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式有误')
        return value

    def validate_allow(self, value):
        """是否同意协议校验"""
        if value != 'true':
            raise serializers.ValidationError("请同意用户协议")
        return value

    def validate(self, attrs):
        """校验密码两个是否相同"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两个密码不一致')

        # 校验验证码
        redis_conn = get_redis_connection('image_code')
        mobile = attrs['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        # 向redis存储数据时都是以字符串进行存储的，取出来都是bytes类型 [bytes]
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')
        # 判断学校 是否存在
        print(attrs)
        school_name = attrs['sch_name']
        if school_name:
            try:
                # print("查询学校名字")
                sch = School.objects.get(sch_name=school_name)
                del attrs['sch_name']
                attrs['schId_id'] = sch.id
            except Exception as e:
                raise serializers.ValidationError('学校错误')
        return attrs

    def create(self, validated_data):
        # 把不需要存储的 password2, sms_code, allow 从字段中移除
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 把密码先取出来
        password = validated_data.pop('password')
        # 根据用户类型，类型1 学生， 类型2 食堂负责人
        user_type = validated_data.pop('user_type')

        if user_type == "1":
            # 类型1 学生
            # 创建用户模型类对象，给模型类中的username 和mobile 属性取值
            user = User(**validated_data)
            user.set_password(password)  # 把密码加密后再赋值给user的password属性
            user.save()  # 保存到数据库
        elif user_type == "2":
            # 类型2 食堂负责人
            user = Canteen(**validated_data)
            user.set_password(password)
            user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler 函数生成payload
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用  生成jwt

        payload = jwt_payload_handler(user)  # 根据user 生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成 完整的jwt

        user.token = token
        return token
