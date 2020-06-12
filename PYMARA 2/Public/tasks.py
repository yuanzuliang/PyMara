"""
    v1.1  ->修复更新漏洞
"""

from django.conf import settings

from PYMARA.celery import app
from blog.models import BlogHistory
import redis

r9 = redis.Redis(db=9, decode_responses=True)


@app.task
def update_blog_info_to_mysql(blog_ids):
    """
        更新mysql
    :param blog_ids:博客id列表
    """
    res_list = []
    # 开启事务
    with r9.pipeline(transaction=True) as pipe:
        pipe.multi()
        # 更新热门列表
        update_rank_hot()
        for blog_id in blog_ids:
            res_list.append(r9.hmget(settings.BLOG_INFO_KEY + str(blog_id),
                                     ['id', 'browse', 'comment', 'praise', 'favorite', 'score']))
            r9.delete(settings.BLOG_INFO_KEY + str(blog_id))
            r9.zrem(settings.BLOG_CACHE_IDS_KEY,blog_id)
        pipe.execute()
    for blog in res_list:
        if blog:
            BlogHistory.objects.filter(blog_id=blog[0]).update(
                browse=blog[1],
                comment=blog[2],
                praise=blog[3],
                favorite=blog[4],
                score=blog[5]
            )

def update_rank_hot():
    """
        更新热门列表
        补足100个
    """
    # 热门列表数量
    count = r9.scard(settings.RANK_HOT_KEY)
    if count >= 100:
        # 更新10个
        r9.spop(settings.RANK_HOT_KEY, 10)
        count -= 10
    for i in range(0, r9.zcard(settings.BLOG_CACHE_IDS_KEY), 10):
        # 获取当前缓存博客活跃度最高的10个
        blog_list = r9.zrange(settings.BLOG_CACHE_IDS_KEY, i, i + 9, desc=True)
        for id in blog_list:
            if r9.sadd(settings.RANK_HOT_KEY, id):
                # 添加成功
                count += 1
                if count == 100:
                    return
    # redis中不足100
    blog_list = BlogHistory.objects.filter(blog__is_show=True, blog__status='1').order_by('score')[:100]
    for blog in blog_list:
        if r9.sadd(settings.RANK_HOT_KEY, blog.id):
            count += 1
            if count == 100:
                return
