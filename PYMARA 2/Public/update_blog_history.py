import redis
from django.conf import settings
from Public.tasks import update_blog_info_to_mysql
from blog.models import Blog, BlogHistory


class UpdateBlogHistory:
    """
        更新博客信息
        获取,更新BlogHistory表信息请使用这个类的方法不要使用ORM操作

        v1.2.0  -->新增主动更新mysql功能  -->新增更新博客功能
        v1.2.1  -->增加类型支持
        v1.2.2  -->更改显示时间
        v1.3.1  -->修复可以为redis中不存在的数据更新属性的bug
        v1.3.2  -->修复时间获取错误的bug
    """

    def __init__(self, r_db=9):
        self._r = redis.Redis(db=r_db, decode_responses=True)

    def __increment_active(self, blog_id):
        self._r.zincrby(settings.BLOG_CACHE_IDS_KEY, 1, blog_id)
        self.__check_cache()

    def __check_cache(self):
        # 判断是否达到更新条件
        if self._r.zcard(settings.BLOG_CACHE_IDS_KEY) >= settings.REDIS_BLOG_INFO_UPDATE:
            self.__update_cache()

    def __update_cache(self):
        # 所有成员id列表
        cache_list = self._r.zrevrange(settings.BLOG_CACHE_IDS_KEY, 0, -1)
        # 判断分数为零的成员数是否大于一半
        count = self._r.zcard(settings.BLOG_CACHE_IDS_KEY) // 2
        if count < self._r.zcount(settings.BLOG_CACHE_IDS_KEY, 0, 0):
            with self._r.pipeline(transaction=True) as pipe:
                pipe.multi()
                # 更新列表
                update_list = self._r.zrange(settings.BLOG_CACHE_IDS_KEY, 0, 0)
                # 从blog_cache_ids中删除分数为0的成员
                self._r.zremrangebyscore(settings.BLOG_CACHE_IDS_KEY, 0, 0)
                pipe.execute()
        else:
            with self._r.pipeline(transaction=True) as pipe:
                pipe.multi()
                # 中位成员
                blog_id = cache_list[count]
                # 中位成员分数
                score = self._r.zscore(settings.BLOG_CACHE_IDS_KEY, blog_id)
                # 获取删除成员列表
                update_list = self._r.zrevrangebyscore(settings.BLOG_CACHE_IDS_KEY, score, 0)
                # 从blog_cache_ids中删除低于中位分数的成员
                self._r.zremrangebyscore(settings.BLOG_CACHE_IDS_KEY, 0, score)
                pipe.execute()
        update_blog_info_to_mysql.delay(update_list)

    def __update_data(self, blog_id, attr, count, amount):
        """
            更新redis数据
        :param attr: 更新的属性
        :param count: 更新的数量 正负整数
        :param amount: 总分增加的倍率
        :return:
        """
        self._insert_redis(blog_id)
        self._r.hincrby(settings.BLOG_INFO_KEY + str(blog_id), attr, int(count))
        self._r.hincrby(settings.BLOG_INFO_KEY + str(blog_id), 'score', int(count) * int(amount))
        # 更新活跃度
        self.__increment_active(blog_id)

    def update_praise(self, blog_id, praise_count=1):
        """
            更新点赞数量
            默认加一
        :param praise_count: 点赞数 正负整数
        :param blog_id: 博客ID
        """
        self.__update_data(blog_id, 'praise', praise_count, settings.SCORE_ALGORITHM['praise'])

    def update_browse(self, blog_id, browse_count=1):
        """
            更新浏览数量
            默认加一
        :param browse_count: 浏览数 正负整数
        :param blog_id: 博客ID
        """
        self.__update_data(blog_id, 'browse', browse_count, settings.SCORE_ALGORITHM['browse'])

    def update_comment(self, blog_id, comment_count=1):
        """
            更新评论数量
            默认加一
        :param blog_id: 博客ID
        :param comment_count: 评论数 正负整数
        """
        self.__update_data(blog_id, 'comment', comment_count, settings.SCORE_ALGORITHM['comment'])

    def update_favorite(self, blog_id, favorite_count=1):
        """
            更新收藏数量
            默认加一
        :param blog_id: 博客ID
        :param favorite_count: 收藏数 正负整数
        :return:
        """
        self.__update_data(blog_id, 'favorite', favorite_count, settings.SCORE_ALGORITHM['comment'])

    def update_blog(self, blog_ids):
        """
            主动更新
        :param blog_id: 博客ID列表
        :return:
        """
        # 推送 celery
        update_blog_info_to_mysql.celery(blog_ids)

    def update_activity(self, blog_id):
        """
            活跃度加一
            不需要更改数据，普通访问时使用
            ps：从redis拿出时使用
        :param blog_ids: 博客ID
        :return:
        """
        self.__increment_active(blog_id)

    def update_status(self, blog_id, status):
        """
            修改博客状态
        :param blog_id:博客ID
        :param status: 状态
        :return: 成功True 失败False
        """
        if str(status) in ['1', '2', '3']:
            if self._r.exists(settings.BLOG_INFO_KEY + str(blog_id)):
                self._r.hset(settings.BLOG_INFO_KEY + str(blog_id), 'status', status)
                self.update_blog([blog_id])
                self.update_activity(blog_id)
                return True
            elif Blog.objects.filter(id=blog_id).update(status=status):
                return True
        return False

    def update_mysql(self):
        """
            更新数据库   ->同步执行
            将redis所有数据写入mysql
        :return:
        """
        print('更新mysql')
        blog_cache_id_list = self._r.zrange(settings.BLOG_CACHE_IDS_KEY, 0, -1)
        update_blog_info_to_mysql(blog_cache_id_list)

    def __get_blog_info_to_mysql(self, blog):
        """
            从mysql获取博客信息
        :param blog: blog对象
        :return: 存有信息的字典
        """
        try:
            blog.bloghistory
        except:
            BlogHistory.objects.create(blog=blog)
        blog_dic = {}
        blog_dic['id'] = blog.id
        blog_dic['title'] = blog.title
        blog_dic['abstract'] = blog.abstract
        blog_dic['original'] = int(blog.original)
        blog_dic['is_blog'] = int(blog.is_blog)
        blog_dic['username'] = blog.user.username
        # 图像对象转换为字符串
        blog_dic['avatar'] = str(blog.user.avatar)
        blog_dic['user_id']=blog.user.id
        blog_dic['praise'] = blog.bloghistory.praise
        blog_dic['browse'] = blog.bloghistory.browse
        blog_dic['comment'] = blog.bloghistory.comment
        blog_dic['favorite'] = blog.bloghistory.favorite
        blog_dic['score'] = blog.bloghistory.score
        blog_dic['create_time'] = str(blog.create_time).split('.')[0]
        blog_dic['status'] = blog.status
        blog_dic['is_show'] = int(blog.is_show)
        if not blog_dic['is_blog']:
            blog_dic['url'] = blog.otherurl.url
        return blog_dic

    def get_blog_info(self, blog_ids, is_show=True, status=1):
        """
            获取博客信息
        :param blog_ids: 一个博客ID列表或者一个博客ID
        :param is_show: 公开状态
        :param status: 博客状态
        :return: 一个装有所有博客信息的列表
        """
        if type(blog_ids) != list:
            if type(blog_ids) == str or type(blog_ids) == int:
                blog_ids = [blog_ids]
            else:
                raise
        blog_list = []
        for blog_id in blog_ids:
            # redis查询
            score = self._r.zscore(settings.BLOG_CACHE_IDS_KEY, blog_id)
            if score or score == 0:
                print('--redis查询--')
                blog_dic = self._r.hgetall(settings.BLOG_INFO_KEY + str(blog_id))
                # 活跃度加1
                self.update_activity(blog_id)
            # mysql查询
            else:
                print('--mysql查询--')
                try:
                    blog = Blog.objects.get(id=blog_id, is_show=is_show, status=status)
                    blog_dic = self.__get_blog_info_to_mysql(blog)
                    # 添加到redis
                    self._r.hmset(settings.BLOG_INFO_KEY + str(blog_id), blog_dic)
                    self._r.zadd(settings.BLOG_CACHE_IDS_KEY, {blog_id: 0})
                except Exception as e:
                    print(e)
                    continue
            # 添加到返回列表中
            blog_list.append(blog_dic)
        return blog_list

    def _insert_redis(self, blog_id):
        """
        主动将mysql里的数据写入redis
        :param blog_id: 博客ID
        :return: 成功True失败False
        """
        print('更新redis')
        score = self._r.zscore(settings.BLOG_CACHE_IDS_KEY, blog_id)
        if score or score == 0:
            return True
        else:
            try:
                blog = Blog.objects.get(id=blog_id)
                blog_dic = self.__get_blog_info_to_mysql(blog)
                # 添加到redis
                self._r.hmset(settings.BLOG_INFO_KEY + str(blog_id), blog_dic)
                self._r.zadd(settings.BLOG_CACHE_IDS_KEY, {blog_id: 0})
                print('redis里没有')
                return True
            except Exception as e:
                print(e)
                return False
