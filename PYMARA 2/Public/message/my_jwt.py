import hmac
import json
import time
import base64
import copy

class Jwt:

    @staticmethod
    def my_encode(my_payload, key, exp=300):
        """
        生成token
        :param my_payload:
        :param key:
        :param exp:
        :return:
        """
        # 1. 定义 header: 固定header写法 -> header转成json字符串 -> json字符串 base64转码后的字节串
        header = {'alg':'HS256', 'typ':'JWT'}
        header_json_str = json.dumps(header, separators=(",",":"), sort_keys=True)
            # dumps 的 separators参数可以去除字符串中无用的空格,值是一个元组
            # 元组的第一个参数是 键值对 之间的分隔符,第二个参数是 键与值 之间的分隔符
            # {"alg":"HS256","typ":"JWT"}
            # dumps 的 sort_keys参数可以使字典有序,便于计算,默认是 False
        header_b64 = Jwt.my_b64encode(header_json_str.encode()) # 字节串

        # 2. 定义　payload: 公有私有声明(dict) -> payload转成json字符串 -> json字符串 base64转码后的字节串
        payload = copy.deepcopy(my_payload) # 深拷贝字典防止改变原字典
        payload["exp"] = time.time() + exp # 结合业务添加过期时间
        payload_json_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        payload_b64 = Jwt.my_b64encode(payload_json_str.encode()) # 字节串

        # 3. 定义 signature:
        hm = hmac.new(key.encode(), header_b64 + b"." + payload_b64, digestmod="SHA256")
        hm_b64 = Jwt.my_b64encode(hm.digest())

        return header_b64 + b"." + payload_b64 + b"." + hm_b64

    @staticmethod
    def my_b64encode(json_bytes):
        """
        自定义b64转码,去掉占位的"="字符
        :param json_bytes: json的字节串
        :return: 去掉"="字符的b64转码后的字节串
        """
        return base64.urlsafe_b64encode(json_bytes).replace(b"=",b"")

    @staticmethod
    def my_decode(my_token, str_key):
        header_b64_bytes, payload_b64_bytes, sign_b64_bytes = my_token.split(b".", 2)

        hm = hmac.new(str_key.encode(), header_b64_bytes+b"."+payload_b64_bytes, digestmod="SHA256")
        if sign_b64_bytes != Jwt.my_b64encode(hm.digest()):
            # 签名不一致, token有问题
            raise Exception("TOKEN IS ERROR")

        # 检查token是否过期
        payload_json_str = Jwt.my_b64decode(payload_b64_bytes).decode()
        payload_json_obj = json.loads(payload_json_str)
        token_exp = payload_json_obj["exp"]
        if time.time() > token_exp:
            raise Exception("TOKEN TIME IS ERROR!")

        return payload_json_obj

    @staticmethod
    def my_b64decode(b64_bytes):
        """
        自定义b64转码,添加去掉的"="字符
        :param b64_bytes:
        :return: 添加"="号的字节串
        """
        count = 4 - (len(b64_bytes) % 4)
        return base64.urlsafe_b64decode(b64_bytes + count * b"=")




if __name__ == '__main__':
    s = Jwt.my_encode({"id": 1, "name": "chenzhuo"}, "123456", 3)
    print(s)


    print(Jwt.my_decode(s, "123456"))



