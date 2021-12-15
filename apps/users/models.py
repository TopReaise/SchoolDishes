from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from utils.myModles import BaseModel


# Create your models here.

class User(AbstractUser):
    sex_choice = ((0, '男'), (1, '女'))
    sex = models.SmallIntegerField(choices=sex_choice, default=0, verbose_name='性别')
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')
    head_photo = models.CharField(max_length=200, default='', verbose_name='头像')
    type_id = models.CharField(max_length=1, null=True, verbose_name="用户类型")

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用戶'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


class Stu(BaseModel):
    user_id = models.ForeignKey('User', related_name='stu', blank=True, on_delete=models.CASCADE,
                                verbose_name='用户ID')
    stu_id = models.CharField(max_length=18, default='00001', verbose_name='学号')
    schId = models.ForeignKey('School', related_name='stus', null=True, blank=True, on_delete=models.SET_NULL,
                              verbose_name='学校ID')

    class Meta:
        db_table = 'tb_stus'
        verbose_name = '学生'
        verbose_name_plural = verbose_name


class School(BaseModel):
    user_id = models.ForeignKey('User', related_name='sch', blank=True, on_delete=models.CASCADE,
                                verbose_name='用户ID')
    sch_name = models.CharField(max_length=120, verbose_name='学校名字')
    sch_code = models.CharField(max_length=18, verbose_name='学校代码')
    sch_id_code = models.CharField(max_length=18, verbose_name='身份证号')


    class Meta:
        db_table = 'tb_school'
        verbose_name = '学校'
        verbose_name_plural = verbose_name


class Canteen(BaseModel):
    user_id = models.ForeignKey('User', related_name='cant', blank=True, on_delete=models.CASCADE,
                                verbose_name='用户ID')
    can_name = models.CharField(max_length=120, verbose_name='食堂名字')
    can_auth = models.SmallIntegerField(default=0, verbose_name='学校认证')
    can_id_code = models.CharField(max_length=18, verbose_name='身份证号')


    class Meta:
        db_table = 'tb_canteen'
        verbose_name = '食堂'
        verbose_name_plural = verbose_name
