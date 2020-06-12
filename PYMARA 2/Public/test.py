from django.db import transaction
from django.http import HttpResponse

from user.models import *

from blog.models import *

# @transaction.atomic
def add_test_data(request):
    User.objects.all().delete()
    with transaction.atomic():
        save_id = transaction.savepoint()
        try:
            user1 = User.objects.create(username='test_username1', avatar='./test.jpg')
            user2 = User.objects.create(username='test_username2', avatar='./test.jpg')
            Login.objects.create(method='1', token='test_password', identifier='test_identifier1',
                                 user=user1)
            Login.objects.create(method='1', token='test_password', identifier='test_identifier2',
                                 user=user2)
            Login.objects.create(method='2', token='test_password', identifier='test_identifier3',
                                 user=user2)
            PasswordHistory.objects.create(password='test_password1', ip='192.0.0.1', method='1', user=user1)
            PasswordHistory.objects.create(password='test_password2', ip='192.0.0.1', method='2', user=user1)
            SecurityQuestion.objects.create(question1='test_question1',question2='test_question2',question3='test_question3',answer1='test_answer1',answer2='test_answer2',answer3='test_answer3',user=user1)
            AvatarHistory.objects.create(avatar='./test.jpg',user=user1)
            Medal.objects.create(name='test',log='./test.jpg',user=user1)
            user_history=UserHistory.objects.create(user=user1)
            LoginHistory.objects.create(ip='127.0.0.1',method=1,user=user1)
            RestrictedFunction.objects.create(user=user1)
            UserInfo.objects.create(name='test_name',user=user1)
            friend=Friend.objects.create(friend_id=1,status=1,user=user1)
            mh=MessageHistory.objects.create(genre='text',friend=friend)
            Message.objects.create(message_history=mh)
            # blog=Blog.objects.create(title='test_title',abstract='test_abstract',author=1,category='python',status='1',user=user1)
            blog=Blog.objects.create(title='test_title',abstract='test_abstract',original=True,author=1,status='1',category='python',is_show=True)
            user1.blog_set.add(blog)
            Content.objects.create(content='test_text',blog=blog)
            Annex.objects.create(name='test_name',filed='./test.jpg',blog=blog)
            Tag.objects.create(tag='test',blog=blog)
            BlogHistory.objects.create(blog=blog)
            BrowserHistory.objects.create(blog=blog,user=user1)
            comment=Comment.objects.create(genre='text',blog=blog,user_history=user_history)
            CommentHistory.objects.create(text='test_text',comment=comment)

            transaction.savepoint_commit(save_id)

        except Exception as e:
            transaction.savepoint_rollback(save_id)
            print(e)
            return HttpResponse('添加失败')

        return HttpResponse('添加成功')


def del_test_data(request):
    try:
        User.objects.all().delete()
        Blog.objects.all().delete()
    except Exception as e:
        print(e)
        return HttpResponse('删除失败')
    return HttpResponse('删除成功')
