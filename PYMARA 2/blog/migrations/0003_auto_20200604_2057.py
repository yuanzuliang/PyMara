# Generated by Django 2.2.12 on 2020-06-04 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20200604_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='活跃'),
        ),
        migrations.AddField(
            model_name='comment',
            name='to_user_id',
            field=models.IntegerField(null=True, verbose_name='评论目标'),
        ),
    ]
