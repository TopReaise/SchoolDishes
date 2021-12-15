from random import randint

from rest_framework import serializers
import re
import hashlib
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from apps.users.models import User, School, Canteen


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    type_id = serializers.CharField(label='用户类型', write_only=True)
    token = serializers.CharField(label='token', read_only=True)
    department_name = serializers.CharField(label="部门名称", required=False)
    people_id_code = serializers.CharField(label="部门负责人身份证", required=False)

    class Meta:
        model = User  # 从User模型类中映射序列化器字段
        fields = ['id', 'username', 'password', 'password2', 'mobile', 'sms_code', 'allow', 'token', 'type_id',
                  "department_name","people_id_code"
                  ]
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
        # 判断

        # try:
        #     if 'sch_name' in attrs:
        #         print("查询学校名字")
        #         school_name = attrs['sch_name']
        #         if school_name != '' and school_name:
        #             sch = School.objects.get(sch_name=str(school_name))
        #             del attrs['sch_name']
        #             attrs['schId_id'] = sch.id
        # except Exception as e:
        #     raise serializers.ValidationError('学校错误')

        return attrs

    def create(self, validated_data):
        # 把不需要存储的 password2, sms_code, allow 从字段中移除
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # print(validated_data)
        # 根据 用户类型 分别存储 数据库，食堂表
        type_id = validated_data["type_id"]
        if type_id == "2" or type_id == "3":
            de_name = validated_data.pop('department_name')
            people_id_code = validated_data.pop('people_id_code')


        # 把密码先取出来
        password = validated_data.pop('password')

        # 创建用户模型类对象，给模型类中的username 和mobile 属性取值
        user = User(**validated_data)
        user.set_password(password)  # 把密码加密后再赋值给user的password属性
        user.save()  # 保存到数据库

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler 函数生成payload
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用  生成jwt

        payload = jwt_payload_handler(user)  # 根据user 生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成 完整的jwt

        user.token = token
        try:
            # 根据type_id 类型 分别存入 sch表， cant食堂表
            if type_id == "2":
                # 存入食堂表
                Canteen.objects.create(user_id=user, can_name=de_name, can_id_code=people_id_code)
            elif type_id == "3":
                scode = "%018d" % randint(0, 999999999999999999)
                School.objects.create(user_id=user, sch_name=de_name, sch_code=scode, sch_id_code=people_id_code)
        except Exception as e:
            print("食堂表或学校表，存入错误")
            print(e)
            raise serializers.ValidationError('食堂表或学校表，存入错误')
        return user


class CreateCanteenSerializer(serializers.ModelSerializer):
    """注册食堂序列化器"""

    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='token', read_only=True)

    class Meta:
        model = Canteen  # 从Canteen模型类中映射序列化器字段
        fields = ['id', 'can_name', 'password', 'password2', 'can_tel', 'sms_code', 'allow', 'token', 'can_addr',
                  'username']
        extra_kwargs = {  # 修改字段选项
            'can_name': {
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
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码'
                }
            }
        }

    def validate_can_tel(self, value):
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
        mobile = attrs['can_tel']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        # 向redis存储数据时都是以字符串进行存储的，取出来都是bytes类型 [bytes]
        if real_sms_code is None or attrs['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('验证码错误')

        return attrs

    def create(self, validated_data):
        # 把不需要存储的 password2, sms_code, allow 从字段中移除
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # input("等待")

        # 把密码先取出来
        password = validated_data.pop('password')
        user = Canteen(**validated_data)

        print("44444")
        # 通过md5 加密密码字段
        md5 = hashlib.md5()
        md5.update(password.encode())
        user.password = md5.hexdigest()
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler 函数生成payload
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER  # 函数引用  生成jwt

        payload = jwt_payload_handler(user)  # 根据user 生成用户相关的载荷
        token = jwt_encode_handler(payload)  # 传入载荷生成 完整的jwt

        user.token = token
        return user
