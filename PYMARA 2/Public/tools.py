from django.http import JsonResponse
import json


def error(code, msg):
    try:
        return JsonResponse({'code': code, 'error': msg})
    except:
        print('error方法')
        print('响应信息转JSON失败')
        return JsonResponse({'code': 200, 'error': '转JSON的时候出错了'})


def success(msg=None,code=200):
    if not msg:
        return JsonResponse({'code': code})
    try:
        return JsonResponse({'code': code, 'data': msg})
    except:
        print('success方法')
        print('响应信息转JSON失败')
        return JsonResponse({'code': code, 'data': '转JSON的时候出错了'})
