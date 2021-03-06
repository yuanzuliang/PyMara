# Generated by Django 2.2.12 on 2020-06-03 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('title', models.CharField(max_length=128, verbose_name='标题')),
                ('abstract', models.CharField(max_length=96, verbose_name='摘要')),
                ('original', models.BooleanField(default=True, verbose_name='原创')),
                ('status', models.CharField(choices=[('1', '已发布'), ('2', '编辑中'), ('3', '已删除')], default='1', max_length=1, verbose_name='状态')),
                ('is_show', models.BooleanField(default=True, verbose_name='展示')),
                ('is_blog', models.BooleanField(default=True, verbose_name='博客类型')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('genre', models.CharField(choices=[('text', '文本'), ('img', '图片'), ('link', '链接')], max_length=4, verbose_name='消息类型')),
                ('child_comment_id', models.IntegerField(null=True, verbose_name='子评论')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='blog.Blog')),
                ('user_history', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.UserHistory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OtherUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('url', models.CharField(max_length=128, unique=True, verbose_name='地址')),
                ('blog', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(default='默认收藏夹', max_length=7, verbose_name='名字')),
                ('public', models.BooleanField(default=True, verbose_name='公开')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('content', models.TextField(verbose_name='博客内容')),
                ('blog', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('text', models.CharField(max_length=1024, null=True, verbose_name='文本')),
                ('img', models.ImageField(null=True, upload_to='img/comment', verbose_name='图片')),
                ('link', models.CharField(max_length=128, null=True, verbose_name='链接')),
                ('comment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='blog.Comment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.CharField(db_index=True, max_length=16, verbose_name='分类')),
                ('blog', models.ManyToManyField(to='blog.Blog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BrowserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('praise', models.BooleanField(default=False, verbose_name='点赞')),
                ('is_active', models.BooleanField(default=True, verbose_name='活跃')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BlogHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('comment', models.IntegerField(default=0, verbose_name='评论')),
                ('favorite', models.IntegerField(default=0, verbose_name='收藏')),
                ('praise', models.IntegerField(default=0, verbose_name='点赞')),
                ('browse', models.IntegerField(default=0, verbose_name='浏览')),
                ('score', models.IntegerField(default=0, verbose_name='总分')),
                ('blog', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='blog.Blog')),
            ],
            options={
                'ordering': ['score'],
            },
        ),
        migrations.CreateModel(
            name='Annex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=16, verbose_name='名字')),
                ('filed', models.FileField(upload_to='annex', verbose_name='文件')),
                ('price', models.DecimalField(decimal_places=1, default=1.0, max_digits=5, verbose_name='价格')),
                ('blog', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='blog.Blog')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
