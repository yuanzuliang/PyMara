"""
    v1.1.0  -->公共时间字段PublicModel修改
"""

from django.db import models
from Public.publicmodel import PublicModel


class User(PublicModel):
    """
        用户核心表
    """
    USER_STATUS_CHOICES = (
        ('0', '正常'),
        ('1', '限制'),
        ('2', '封禁'),
        ('3', '删除'),
    )
    USER_PERMISSION_CHOICES = (
        ('1', '普通'),
        ('2', '会员'),
        ('3', '管理员'),
        ('4', 'GOD')
    )
    # 可以为空,使用登录账号作为昵称,最多8个字符(中英文都为一个字符)
    username = models.CharField(verbose_name='用户名', max_length=16, unique=True)
    # 可以为空,使用默认头像
    avatar = models.ImageField(verbose_name='头像', upload_to='avatar', default='default.jpg')
    status = models.SmallIntegerField(verbose_name='状态', choices=USER_STATUS_CHOICES, default='0')
    permission = models.SmallIntegerField(verbose_name='权限', choices=USER_PERMISSION_CHOICES, default='1')


class Login(PublicModel):
    """
        万能登录表
        用户表一对多
    """

    LOGIN_METHOD_CHOICES = (
        ('1', '邮箱'),
        ('2', '手机号'),
        ('3', '微博'),
        ('4', 'QQ'),
        ('5', '微信'),
    )
    method = models.CharField(verbose_name='登录方式', choices=LOGIN_METHOD_CHOICES, max_length=1)
    identifier = models.CharField(verbose_name='唯一标示', max_length=16, unique=True)
    token = models.CharField(verbose_name='登录令牌', max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)


class PasswordHistory(PublicModel):
    """
        历史密码表
        用户表表一对多
    """
    PASSWORD_CHANGE_METHOD_CHOICES = (
        ('1', '邮箱'),
        ('2', '手机'),
        ('3', '密保'),
    )
    password = models.CharField(verbose_name='密码', max_length=32)
    ip = models.CharField(verbose_name='IP', max_length=39)
    method = models.CharField(verbose_name='修改方式', choices=PASSWORD_CHANGE_METHOD_CHOICES, max_length=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class SecurityQuestion(PublicModel):
    """
        密保问题及答案表
        用户表一对一
    """
    question1 = models.CharField(verbose_name='问题一', max_length=16)
    question2 = models.CharField(verbose_name='问题二', max_length=16)
    question3 = models.CharField(verbose_name='问题三', max_length=16)
    answer1 = models.CharField(verbose_name='答案一', max_length=16)
    answer2 = models.CharField(verbose_name='答案二', max_length=16)
    answer3 = models.CharField(verbose_name='答案三', max_length=16)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class AvatarHistory(PublicModel):
    """
        历史头像表
        用户表一对多
    """
    avatar = models.ImageField(verbose_name='头像', upload_to='avatar_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Medal(PublicModel):
    """
        勋章表
        用户表一对多
    """
    MEDAL_LEVEL_CHOICES = (
        ('1', 'LEVEL 1'),
        ('2', 'LEVEL 2'),
        ('3', 'LEVEL 3'),
        ('4', 'LEVEL 4'),
        ('5', 'LEVEL 5'),
        ('6', 'LEVEL 6'),
    )
    name = models.CharField(verbose_name='名称', max_length=4)
    level = models.CharField(verbose_name='等级', choices=MEDAL_LEVEL_CHOICES, max_length=1, default='1')
    log = models.ImageField(verbose_name='图标', upload_to='log')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class UserHistory(PublicModel):
    """
        用户记录表
        用户表一对一
    """
    original = models.IntegerField(verbose_name='原创', default=0)
    comments = models.IntegerField(verbose_name='评论', default=0)
    favorite = models.IntegerField(verbose_name='收藏', default=0)
    praise = models.IntegerField(verbose_name='点赞', default=0)
    browse = models.IntegerField(verbose_name='浏览', default=0)
    fans = models.IntegerField(verbose_name='粉丝', default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class LoginHistory(PublicModel):
    """
        登录历史表
        用户表一对多
    """
    LOGIN_METHOD_CHOICES = (
        ('1', '邮箱'),
        ('2', '手机号'),
        ('3', '微博'),
        ('4', 'QQ'),
        ('5', '微信'),
    )
    ip = models.CharField(verbose_name='IP', max_length=39)
    method = models.CharField(verbose_name='登录方式', choices=LOGIN_METHOD_CHOICES, max_length=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class RestrictedFunction(PublicModel):
    """
        功能限制表
        用户表一对一
    """
    entry = models.BooleanField(verbose_name='登录', default=False)
    comment = models.BooleanField(verbose_name='评论', default=False)
    silence = models.BooleanField(verbose_name='聊天', default=False)
    upload = models.BooleanField(verbose_name='发博客', default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class UserInfo(PublicModel):
    """
        用户个人资料表
        用户表一对一
    """
    USER_SEX_CHOICES = (
        ('1', '男'),
        ('2', '女'),
        ('3', '影藏')
    )
    name = models.CharField(verbose_name='姓名', max_length=16, null=True)
    age = models.CharField(verbose_name='年龄', max_length=3, null=True)
    sex = models.CharField(verbose_name='性别', choices=USER_SEX_CHOICES, null=True, max_length=1)
    birthday = models.DateField(verbose_name='生日', null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Friend(PublicModel):
    """
        好友表
        用户表一对多
    """
    friend_id = models.IntegerField(verbose_name='好友ID')
    dialogue = models.BooleanField(verbose_name='允许发送消息', default=True)
    status = models.BooleanField(verbose_name='好友状态', default=False)
    blacklist = models.BooleanField(verbose_name='黑名单', default=False)
    group = models.CharField(verbose_name='组名', default='我的好友', max_length=7)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class MessageHistory(PublicModel):
    """
        好友聊天记录表
        好友表一对多
    """
    MESSAGE_GENRE_CHOICES = (
        ('text', '文本'),
        ('img', '图片'),
        ('link', '链接'),
    )
    genre = models.CharField(verbose_name='消息类型', choices=MESSAGE_GENRE_CHOICES, max_length=4, )
    is_active = models.BooleanField(verbose_name='活跃', default=True)
    friend = models.ForeignKey(Friend, on_delete=models.CASCADE)


class Message(PublicModel):
    """
        消息表
        好友聊天记录表一对一
    """
    text = models.CharField(verbose_name='文本', max_length=1024, null=True)
    img = models.ImageField(verbose_name='图片', upload_to='img/message', null=True)
    link = models.CharField(verbose_name='链接', max_length=128, null=True)
    message_history = models.OneToOneField(MessageHistory, on_delete=models.CASCADE)
