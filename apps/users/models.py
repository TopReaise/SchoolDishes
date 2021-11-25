from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from utils.myModles import BaseModel


# Create your models here.

class User(AbstractUser):
    sex_choice = (('0', '男'), ('1', '女'))
    sex = models.CharField(max_length=1, choices=sex_choice, default=0, verbose_name='性别')
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')
    head_photo = models.CharField(max_length=120, default='', verbose_name='头像')
    stu_id = models.CharField(max_length=18, default='00001', verbose_name='学号')
    schId = models.ForeignKey('School', related_name='stus', null=True, blank=True, on_delete=models.SET_NULL,
                              verbose_name='学校ID')

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


class School(BaseModel):
    sch_name = models.CharField(max_length=120, verbose_name='学校名字')
    sch_addr = models.CharField(max_length=120, verbose_name='学校地址')
    sch_tel = models.CharField(max_length=11, verbose_name='学校电话')
    sch_head = models.CharField(max_length=120, default='', verbose_name='头像')
    sch_code = models.CharField(max_length=18, verbose_name='学校代码')
    sch_people = models.CharField(max_length=15, verbose_name='学校负责人')
    class Meta:
        db_table = 'tb_school'
        verbose_name = '学校'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


class Canteen(BaseModel):
    can_name = models.CharField(max_length=120, verbose_name='食堂名字')
    can_addr = models.CharField(max_length=120, verbose_name='食堂地址')
    can_tel = models.CharField(max_length=11, verbose_name='食堂电话')
    can_head = models.CharField(max_length=120, default='', verbose_name='头像')
    can_people = models.CharField(max_length=15, verbose_name='食堂负责人')

    class Meta:
        db_table = 'tb_canteen'
        verbose_name = '食堂'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']





