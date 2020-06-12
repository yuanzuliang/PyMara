import json

import requests
headers={'pymaratoken':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1OTEzNTY0MzAuMjczMDE1NSwiaWQiOjIsInBob25lIjoiMTU5NzIxNjc3MjQifQ.eLh94f3sAYtpIkIS-qdV-r7Gi279c10J3muKAVgiCw4'}
url='http://127.0.0.1:8000/v1/blog/display/1/'
# 浏览文章  -->测试通过
# print(json.loads(requests.get(url=url+'info',headers=headers).text))

# 点赞  -->测试通过
# print(json.loads(requests.patch(url=url+'praise',headers=headers).text))

# 发评论  -->测试通过
# data=json.dumps({'type':'text','comment_info':'这是post发的一级评论'})
# data=json.dumps({'type':'text','comment_info':'这是post发的二级评论','to_user_id':'2','parent_comment_id':'130'})
# print(json.loads(requests.post(url=url+'comment',data=data,headers=headers).text))

