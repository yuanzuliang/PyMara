"""
登录令牌
{'code': 403, 'error': '登录信息过期'}
{'code': 444, 'error': '账号权限被限制'}
"""

import copy
import json
import base64
import time
import hmac
from django.http import JsonResponse
from django.conf import settings
from user.models import User


def logging_check(fun):
    def wrapper(self, request, *args, **kwargs):
        token = request.META.get('HTTP_PYMARATOKEN')
        if not token:
            return JsonResponse({'code': 403, 'error': '请登录!'})
        try:
            payload = Jwt().my_decode(token, settings.JWT_TOKEN_KEY)
        except:
            return JsonResponse({'code': 403, 'error': '登录信息过期'})
        id = payload['id']  # 登录用户的id
        phone = payload["phone"]  # 登录用户的手机号(本项目的账号)

        # 如果body里有参数
        if request.body:
            json_obj = json.loads(request.body.decode())
            request.my_data = json_obj  # 视图函数从这里取, json对象
        try:
            user = User.objects.get(id=id, status=0)
            request.my_user = user  # 登录的用户对象, MyModel对象(User表实例)
            request.my_user_phone = phone  # 登录用户的手机号(本项目的唯一注册账号)
        except:
            return JsonResponse({'code': 444, 'error': '账号权限被限制'})
        print('---通过验证---')
        return fun(self, request, *args, **kwargs)
    return wrapper


def user_check(request):
    token = request.META.get('HTTP_PYMARATOKEN')
    if not token:
        return False
    try:
        payload = Jwt().my_decode(token, settings.JWT_TOKEN_KEY)
        request.user = User.objects.get(id=payload['id'])
        print('用户校验通过')
        return True
    except:
        print('用户校验失败')
        return False


class Jwt:
    def __init__(self):
        pass

    @staticmethod
    def my_encode(my_payload, key, exp=3600 * 24):
        """
        制作token令牌
        :param my_payload:私有声明
        :param key: token_key
        :param exp: 有效时间
        :return: str 字符串类型token
        """
        header = {'alg': 'HS256', 'typ': 'JWT'}
        header_json_str = json.dumps(header, separators=(',', ':'), sort_keys=True)
        header_b64_bytes = Jwt.my_b64encode(header_json_str.encode())

        payload = copy.deepcopy(my_payload)
        payload['exp'] = time.time() + exp
        payload_json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        payload_b64_bytes = Jwt.my_b64encode(payload_json_str.encode())

        hm = hmac.new(key.encode(), header_b64_bytes + b'.' + payload_b64_bytes, digestmod='SHA256')
        hm_bs = Jwt.my_b64encode(hm.digest())
        return (header_b64_bytes + b"." + payload_b64_bytes + b"." + hm_bs).decode()

    @staticmethod
    def my_b64encode(j_s):
        return base64.urlsafe_b64encode(j_s).replace(b'=', b'')

    @staticmethod
    def my_decode(token_str, key):
        """
        校验token令牌
        :param token_str:
        :param key:
        :return: dict payload对象
        """
        token = token_str.encode()
        header_bs, payload_bs, sign_bs = token.split(b'.')
        hm = hmac.new(key.encode(), header_bs + b'.' + payload_bs, digestmod='SHA256')
        if Jwt.my_b64encode(hm.digest()) != sign_bs:
            raise
        # 校验时间
        payload_json = Jwt.my_b64decode(payload_bs)
        payload = json.loads(payload_json)
        exp = payload['exp']
        if time.time() > exp:
            print('过期')
            raise Exception('过期')
        return payload

    @staticmethod
    def my_b64decode(b_s):
        rem = len(b_s) % 4
        b_s += b'=' * (4 - rem)
        return base64.urlsafe_b64decode(b_s)
