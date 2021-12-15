import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_dishes.settings")# project_name 项目名称
django.setup()

import hashlib
from random import randint

from apps.users.models import School, User


def cre_sch():
    sch_name = input("请输入学校名字")
    username = input("请输入用户名")
    mobile = input("请输入电话")
    people_id = input("请输入负责人身份证号码")



    try:
        # 根据手机号和 用户名查询 用户
        user = User.objects.get(username=username, mobile=mobile)

        sch = School.objects.create(user_id=user,sch_name=sch_name, sch_code=scode, sch_id_code=people_id)
        print(sch)
        print("写入成功")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    cre_sch()

