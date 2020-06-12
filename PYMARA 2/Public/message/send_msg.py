import json

import Public.message.zhenzismsclient as smsclient


class Message:

    apiUrl = "https://sms_developer.zhenzikj.com"
    appId = "105719"
    appSecret = "OTllMjgxMDMtMzhiNy00ZDU1LWI1MjItNThjZDljYmI1ODhi"

    client = smsclient.ZhenziSmsClient(apiUrl, appId, appSecret)

    def send_message(self, phone_num, code, templateId="141", time="五"):
        """
            发送短信验证码
        :param phone_num: str 收件人手机号
        :param code:  str 6位随机激活码
        :param templateId: str 榛子云短信平台模板id
        :param time: str 过期时间，仅用于显示
        :return: json_str 短信发送结果
        """
        if phone_num and code:
            params = {}
            params['number'] = phone_num
            params['templateId'] = templateId
            params['templateParams'] = [code, time]

            json_str_data = self.client.send(params)
            return json_str_data
        else:
            raise Exception("手机号和验证码不能为空")

    def number_of_message(self):
        """
            查询剩余短语条数
            返回结果是json格式的字符串,
            code: 查询状态，0为成功，
            data: 为剩余短信条数。
            非0为查询失败，可从data中查看错误信息
        """
        result = json.loads(self.client.balance())

        code = result["code"]
        data = result["data"]

        if not code:
            print("短信剩余{}条".format(data))
        else:
            print("错误代码: {}, {}".format(code, data))



if __name__ == '__main__':
    m = Message()
    # m.send_message("13006370870", "666666")
    m.number_of_message()
