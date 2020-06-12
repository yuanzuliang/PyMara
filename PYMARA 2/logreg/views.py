"""
{"code": 601, "error":"手机号不可用"}
{"code": 602, "error": "短信平台发送短信失败"}
{"code": 603, "error": "验证码校验失败"}
{"code": 604, "error": "用户注册失败(mysql create user error)"}
{"code": 605, "error": "用户注册失败,验证码校验失败"}
{"code": 606, "error": "用户登录失败,缺少账号或密码"}
{"code": 607, "error": "用户登录失败,账号或密码错误"}
{"code": 608, "error": "用户登录失败,账号不存在"}
{"code": 609, "error": "用户登录失败,账号或密码有误"}
{"code": 610, "error": "用户登录失败,用户账号状态异常"}
{"code": 611, "error": "验证码写入redis失败"}
{"code": 612, "error": "校验失败,缺少手机号或验证码"}
{"code": 613, "error": "校验失败,验证码有误"}
{"code": 614, "error": "新密码mysql存储失败"}
{"code": 615, "error": "手机号未注册"}
{"code": 616, "error": "微博服务器正忙"}
{"code": 617, "error": "微博返回有误"}
{"code": 618, "error": "微博关联失败"}
"""

import re
import json
import time
import random
import requests

from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.core.cache import caches

from Public.message.send_email_465 import SendEmail
from Public.message.send_msg import Message
from Public.publictoken import Jwt

from user.models import User, Login
from urllib.parse import urlencode


class JudgePhoneNumber(View):

    def post(self, request):

        phone_num_obj = json.loads(request.body.decode())
        phone_num = phone_num_obj.get("phone_number")

        if not phone_num:
            return JsonResponse({"code": 613, "error": "校验失败,手机号有误"})

        try:
            old_data = Login.objects.get(identifier=phone_num, method="2")
        except Exception as e:
            # 未查询到手机号的注册记录，手机号可以注册
            return JsonResponse({"code": 200, "data": "手机号可用"})

        # TODO 暂未校验用户的状态 现在是只要查到库里有这个手机号　就不允许注册
        return JsonResponse({"code": 601, "error":"手机号不可用"})


class SendMessage(View):

    """
        短信返回错误信息对应查询
        100	参数格式错误	检查请求参数是否为空, 或手机号码格式错误
        101	短信内容超过1000字	短信内容过长，请筛检或分多次发送
        105	appId错误或应用不存在	请联系工作人员申请应用或检查appId是否输入错误
        106	应用被禁止	请联系工作人员查看原因
        107	ip错误	如果设置了ip白名单，系统会检查请求服务器的ip地址，已确定是否为安全的来源访问
        108	短信余额不足	需要到用户中心进行充值
        109	今日发送超过限额	如果设置了日发送数量，则每个接收号码不得超过这个数量
        110	应用秘钥(AppSecret)错误	检查AppSecret是否输入错误，或是否已在用户中心进行了秘钥重置
        111	账号不存在	请联系工作人员申请账号
        1000 系统位置错误	请联系工作人员或技术人员检查原因
    """

    def create_random_number(self):
        return str(random.randint(100000, 999999))

    def send_error_email_to_manager(self, phone_num, code="xxx", data="未知问题"):
        dict_way = {
            100: "检查请求参数是否为空, 或手机号码格式错误",
            101: "短信内容过长，请筛检或分多次发送",
            105: "请联系工作人员申请应用或检查appId是否输入错误",
            106: "请联系工作人员查看原因",
            107: "如果设置了ip白名单，系统会检查请求服务器的ip地址，已确定是否为安全的来源访问",
            108: "需要到用户中心进行充值",
            109: "如果设置了日发送数量，则每个接收号码不得超过这个数量",
            110: "检查AppSecret是否输入错误，或是否已在用户中心进行了秘钥重置",
            111: "请联系工作人员申请账号",
            1000: "请联系工作人员或技术人员检查原因",
        }
        way = dict_way.get(code, "未知原因，请联系工作人员，迅速解决!")

        from_email = "1102225813@qq.com"
        from_pass = "evstyhswxsawjada"
        list_addrs = [("陈卓小号", "783753616@qq.com"),
                      ("袁祖亮", "1344748066@qq.com"),
                      ("李慧民", "527181835@qq.com"),
                      ("刘华兴", "669177285@qq.com"), ]
        error_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        email_text = """
            <h2>
                错误类型: 用户注册短信验证码服务器发送失败<br>
                错误时间: {}<br>
                注册账户: {}<br>
                错误代码: {}<br>
                错误原因: {}<br>
                解决方式: {}
            </h2> 
        """.format(error_time ,phone_num, code, data, way)

        email_obj = SendEmail(my_email=from_email, my_pass=from_pass, list_addr=list_addrs)
        res = email_obj.mail(email_text, "【PyMara报错邮件】")

        if res:
            print("注册报错邮件发送成功")
        else:
            print("注册报错邮件发送失败")

    def post(self, request):

        phone_num_obj = json.loads(request.body.decode())
        phone_num = str(phone_num_obj["phone_number"])
        info = str(phone_num_obj.get("info"))

        str_key = "register:{}"
        if info == "findPsd":
            str_key = "findpsd:{}"

        ran_num = self.create_random_number()

        try:
            # 在此处将验证码存入 redis,过期时间　300秒

            # TODO redis 方案二
            CACHE_15 = caches["cache_15"]
            redis_15_key = str_key.format(phone_num)
            CACHE_15.set(redis_15_key, ran_num, 300)

        except Exception as e:
            print("------redis set random number error-------")
            print(e)
            return JsonResponse({"code": 611, "error": "验证码写入redis失败"})

        # 发送手机验证码
        msh_obj = Message()
        res_str = msh_obj.send_message(phone_num, ran_num)
        res_obj = json.loads(res_str)

        code = res_obj["code"]
        data = res_obj["data"]

        if code:
            # 此时用户验证短信发送失败 自动发系统报错邮件 到管理员邮箱
            self.send_error_email_to_manager(phone_num, code, data)
            return JsonResponse({"code": 602, "error": "短信平台发送短信失败"})

        return JsonResponse({"code": 200, "data": "发送成功,请在手机端查收"})


class Register(View):

    def judge_msg_number(self, redis_15_key, msg_num):
        """
            校验用户验证码
        :param redis_15_key: str key
        :param msg_num: str 验证码
        :return:  True 校验成功  False 校验失败
        """
        # TODO redis 查询方式一 有可能修改
        # import redis
        # r = redis.Redis(db=db)
        # result = r.get(redis_15_key)
        # 没查询到返回 None
        # 注意　None.decode() 会报错 AttributeError: 'NoneType' object has no attribute 'decode'
        # 找到则返回value的字节串 b'234453'

        # TODO redis 查询方式二
        CACHE_15 = caches["cache_15"]
        str_num = CACHE_15.get(redis_15_key) # str　字符串类型的结果

        if str_num:
            if msg_num == str_num:
                return True
            return False
        return False

    def hash_md5_psd(self, str_psd):
        """
            将明文密码通过 md5算法转成密文存储
        :param psd: str 明文密码
        :return: str 转换后的密文密码
        """
        import hashlib
        m = hashlib.md5()
        m.update(str_psd.encode())  # 注意此处应是字节串
        return m.hexdigest()

    def post(self, request):

        msg_obj = json.loads(request.body.decode())
        str_msg_num = str(msg_obj["msg_num"])
        str_phone_num = str(msg_obj["phone_num"])

        redis_15_key = "register:{}".format(str_phone_num)

        if self.judge_msg_number(redis_15_key, str_msg_num):
            # 校验成功　可以写入数据库
            str_psd = str(msg_obj["psd"])
            uname = "py_{}".format(str_phone_num)
            hash_psd = self.hash_md5_psd(str_psd)

            # TODO 是否需要开事务
            # 开启事务
            with transaction.atomic():
                # 禁止自动提交
                save_id = transaction.savepoint() # 创建保存点,记录当前的状态
                try:
                    new_user = User.objects.create(username=uname)
                    new_user.login_set.create(method=2, identifier=str_phone_num, token=hash_psd)
                except Exception as e:
                    print("------- mysql create user error -------")
                    print(e)
                    transaction.savepoint_rollback(save_id) # 失败回滚
                    return JsonResponse({"code": 604, "error": "用户注册失败(mysql create user error)"})
                # 提交
                transaction.savepoint_commit(save_id)
                return JsonResponse({"code": 200, "data": "用户注册成功"})
        return JsonResponse({"code": 605, "error": "用户注册失败,验证码校验失败"})


class UserLogin(View):

    def judge_data(self, str_re, str_word):
        re_res = re.findall(str_re, str_word)
        if re_res and len(re_res) == 1 and re_res[0] == str_word:
            return True
        return False

    def post(self, request):
        user_obj = json.loads(request.body.decode())
        phone = user_obj.get("phone_number")
        psd = user_obj.get("password")

        if not phone or not psd:
            return JsonResponse({"code": 606, "error": "用户登录失败,缺少账号或密码"})

        # 后端校验数据
        if not self.judge_data(r"1[0-9]{10}", phone) and not self.judge_data(r"[0-9a-zA-Z_]{8,16}", psd):
            return JsonResponse({"code": 607, "error": "用户登录失败,账号或密码错误"})

        hash_psd = Register().hash_md5_psd(psd)
        try:
            old_psd = Login.objects.get(identifier=phone)
        except Exception as e:
            print("------Login get error------")
            print(e)
            return JsonResponse({"code": 608, "error": "用户登录失败,账号不存在"})
        # print("------status------")
        # print(old_psd.user.status, type(old_psd.user.status))
        # 0 <class 'int'>

        if hash_psd == old_psd.token:
            if old_psd.user.status == 0:
                # TODO 签发 token
                jwt_obj = Jwt()
                str_token = jwt_obj.my_encode({"id":old_psd.user.id, "phone":old_psd.identifier}, settings.JWT_TOKEN_KEY)
                dict_data = {"code": 200,
                             "data": str_token,
                             "id":old_psd.user.id,
                             "uname":old_psd.user.username,
                             "phone": old_psd.identifier}
                return JsonResponse(dict_data)

            return JsonResponse({"code": 610, "error": "用户登录失败,用户账号状态异常"})

        return JsonResponse({"code": 609, "error": "用户登录失败,账号或密码有误"})


class FindPsd(View):

    def post(self, request):
        msg_obj = json.loads(request.body.decode())
        str_msg_num = msg_obj.get("msg_number")
        str_phone_num = msg_obj.get("phone_number")

        if not str_phone_num or not str_msg_num:
            return JsonResponse({"code": 612, "error": "校验失败,缺少手机号或验证码"})

        str_key = "findpsd:{}".format(str_phone_num)
        res = Register().judge_msg_number(str_key, str_msg_num)

        if res:
            return JsonResponse({"code":200, "data":str_phone_num})

        return JsonResponse({"code": 613, "error": "校验失败,验证码有误"})


class ChangePsd(View):

    def post(self, request):
        psd_obj = json.loads(request.body.decode())
        str_psd_1 = psd_obj.get("psd1")
        str_psd_2 = psd_obj.get("psd2")
        str_phone = psd_obj.get("phone")
        if not str_psd_1 or not str_psd_2 or not str_phone:
            return JsonResponse({"code": 606, "error": "用户登录失败,缺少账号或密码"})
        if str_psd_1 != str_psd_2:
            return JsonResponse({"code": 609, "error": "用户登录失败,账号或密码有误"})

        # 将数据库中的密码修改
        new_psd = Register().hash_md5_psd(str_psd_1)

        try:
            old_user = Login.objects.get(identifier=str_phone, user__status=0)
            old_user.token = new_psd
            old_user.save()
        except Exception as e:
            print("-------change new psd error-------")
            print(e)
            return JsonResponse({"code": 614, "error": "新密码mysql存储失败"})

        return JsonResponse({"code": 200, "data": "重置成功"})


class JudgeOldPhone(View):

    def post(self, request):
        phone_num_obj = json.loads(request.body.decode())
        phone_num = phone_num_obj.get("phone_number")

        if not phone_num:
            return JsonResponse({"code": 613, "error": "校验失败,手机号有误"})

        try:
            old_data = Login.objects.get(identifier=phone_num, method="2", user__status=0)
        except Exception as e:
            return JsonResponse({"code": 615, "error": "手机号未注册"})
        return JsonResponse({"code": 200, "error":"手机号状态正常,可修改密码"})


class WeiboLoginView(View):

    def get(self, request):
        # https://api.weibo.com/oauth2/authorize
        # ?client_id=YOUR_CLIENT_ID
        # &response_type=code
        # &redirect_uri=YOUR_REGISTERED_REDIRECT_URI

        weibo_url = "https://api.weibo.com/oauth2/authorize"

        dict_params = {"client_id":settings.MY_WB_APP_KEY,
                       "response_type":"code",
                       "redirect_uri":settings.MY_WB_REDIRECT_URI}

        weibo_login_url = "{}?{}".format(weibo_url, urlencode(dict_params))
        return JsonResponse({"code": 200, "data":weibo_login_url})


class WeiboUserView(View):

    def get(self, request):
        weibo_code = request.GET.get("code")
        print("----------------")
        print(weibo_code)
        if not weibo_code:
            return JsonResponse({"code":403, "error": "回调error"})

        token_url = "https://api.weibo.com/oauth2/access_token"

        req_data = {
            "client_id": settings.MY_WB_APP_KEY,
            "client_secret": settings.MY_WB_APP_SECRET,
            "grant_type": "authorization_code",
            "code": weibo_code,
            "redirect_uri": settings.MY_WB_REDIRECT_URI # 回调地址
        }

        response = requests.post(url=token_url, data=req_data)
        resp_obj = json.loads(response.text)
        if response.status_code != 200 or resp_obj.get("error"):
            return JsonResponse({"code": 616, "error": "微博服务器正忙"})

        access_token = resp_obj.get("access_token")
        weibo_uid = resp_obj.get("uid")

        if not access_token or not weibo_uid:
            return JsonResponse({"code": 617, "error": "微博返回有误"})

        # 注意：数据库中各种登录账号存在同一个字段里, 而且具有唯一索引,
        # 微博uid为纯数字格式,以免与其他账号冲突, 所以添加 'w_'字符作为唯一标识
        my_weibo_uid = "w_{}".format(weibo_uid)
        # 微博登录成功, token, uid获取成功, 写入数据库
        try:
            weibo_user = Login.objects.get(identifier=my_weibo_uid, method="3")
        except Exception as e:
            # 未查询到用户记录, 该用户第一次登录, 此时还没有关联PyMara内部账号, 外键关联为空
            Login.objects.create(method="3", identifier=my_weibo_uid, token=access_token)
            # 需要做关联注册,　带回 my_weibo_uid, 用作关联内部用户
            return JsonResponse({"code": 302, "data": my_weibo_uid})
        else:
            old_pymara_user = weibo_user.user

            if old_pymara_user:
                # 微博账号,关联过内部用户, 用内部用户账号登录
                if old_pymara_user.status != 0:
                    return JsonResponse({"code": 610, "error": "用户登录失败,用户账号状态异常"})
                # TODO 用户状态正常 签发 token
                old_user_phone = Login.objects.get(user=old_pymara_user, method="2").identifier
                jwt_obj = Jwt()
                str_token = jwt_obj.my_encode({"id":old_pymara_user.id, "phone":old_user_phone}, settings.JWT_TOKEN_KEY)

                dict_data = {"code": 200,
                             "data": str_token,
                             "id": old_pymara_user.id,
                             "uname": old_pymara_user.username,
                             "phone": old_user_phone,
                             "wuid":weibo_user.identifier}
                return JsonResponse(dict_data)
            else:
                # 微博账号,没有关联过内部用户,需要做关联注册
                return JsonResponse({"code": 302, "data": my_weibo_uid})


# 微博登录绑定PyMara用户
class BindPymaraUser(View):

    def judge_data(self, str_re, str_word):
        re_res = re.findall(str_re, str_word)
        if re_res and len(re_res) == 1 and re_res[0] == str_word:
            return True
        return False

    def post(self, request, wuid):
        user_obj = json.loads(request.body.decode())
        phone = user_obj.get("phone_number")
        psd = user_obj.get("password")

        if not phone or not psd or not wuid:
            return JsonResponse({"code": 606, "error": "用户登录失败,缺少账号或密码"})

        # 后端校验数据
        if not self.judge_data(r"1[0-9]{10}", phone) and not self.judge_data(r"[0-9a-zA-Z_]{8,16}", psd):
            return JsonResponse({"code": 607, "error": "用户登录失败,账号或密码错误"})

        hash_psd = Register().hash_md5_psd(psd)
        try:
            old_login = Login.objects.get(identifier=phone)
        except Exception as e:
            print("------Login get error------")
            print(e)
            return JsonResponse({"code": 608, "error": "用户登录失败,账号不存在"})

        if hash_psd == old_login.token:
            if old_login.user.status == 0:
                # TODO 将微博账号与用户关联
                try:
                    weibo_login = Login.objects.get(identifier=wuid)
                    weibo_login.user = old_login.user
                    weibo_login.save()
                except Exception as e:
                    print("--------------")
                    print(e)
                    return JsonResponse({"code": 618, "error": "微博关联失败"})

                # 绑定成功
                jwt_obj = Jwt()
                str_token = jwt_obj.my_encode({"id":weibo_login.user.id, "phone":old_login.identifier}, settings.JWT_TOKEN_KEY)

                dict_data = {"code": 200,
                             "data": str_token,
                             "id":weibo_login.user.id,
                             "uname":weibo_login.user.username,
                             "phone": old_login.identifier,
                             "wuid":weibo_login.identifier}
                return JsonResponse(dict_data)

            return JsonResponse({"code": 610, "error": "用户登录失败,用户账号状态异常"})

        return JsonResponse({"code": 609, "error": "用户登录失败,账号或密码有误"})




