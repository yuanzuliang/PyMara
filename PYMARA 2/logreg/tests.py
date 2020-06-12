from django.test import TestCase

# Create your tests here.

# import redis
#
# r = redis.Redis(db=15)
# result = r.get("redis2")
# print(result.decode())
#　没找到返回 None
#　找到则返回value的字节串 b'234453'


# import hashlib
# m = hashlib.md5()
# m.update(b"12345678") #注意此处应是字节串
# passwrd_h = m.hexdigest()
# print(passwrd_h, type(passwrd_h))
#输出
# 25d55ad283aa400af464c76d713c07ad <class 'str'>


# import time
# print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
# 2020-05-21 15:01:16

# import re
#
# # str1 = "1300637087012355559999"
# # str2 = "sddddddddddd"
#
# # re1 = re.findall(r"1[0-9]{10}", str1)
# #
# # if re1 and len(re1) == 1 and re1[0] == str1:
# #     print(re1[0])
# # else:
# #     print(re1, "error")
#
# # re_psd = re.findall(r"[0-9a-zA-Z_]{8,16}", str2)
# # if re_psd and len(re_psd) == 1 and re_psd[0] == str2:
# #     print(re_psd[0])
# # else:
# #     print(str2, "error")
#
# def judge_data(str_re, str_word):
#     re_res = re.findall(str_re, str_word)
#     if re_res and len(re_res) == 1 and re_res[0] == str_word:
#         return True
#     return False
#
# str1 = "1300637087012355559999"
# str2 = "12345678"
#
# print(judge_data(r"[0-9a-zA-Z_]{8,16}", str2))


# from Public.publictoken import Jwt
# from django.conf import settings
#
# j = Jwt()
# token = j.my_encode({"id":"1","username": "13006370870"}, "0TLNWooggVcDzSkK")
# print(token)
# print(type(token))

# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTAyMjU1ODguMDA1Nzc5NSwiaWQiOiIxIiwidXNlcm5hbWUiOiIxMzAwNjM3MDg3MCJ9.F2YkDGNo5OIt-2GAYT-BiZHjB-pOy7265gwabO_Zf_4"
#
# res = j.decode(token, settings.JWT_TOKEN_KEY)
# print(res)

# ph = {"name":"chenzhuo", "info": "pshh"}
# info = ph.get("info1")
# print(info, type(info))
# if not info:
#     print("aaa")
# else:
#     print("bbb")

