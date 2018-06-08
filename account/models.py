from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

class Contact(models.Model):

    # 创建关系的用户
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rel_from_set')
    # 被关注的用户
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rel_to_set')
    # 关系创建时的时间
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)


User.add_to_class(
    'following',
    models.ManyToManyField('self',
                           # 指定Django 模型来表示你想要使用的中介表
                           through=Contact,
                           related_name='followers',
                           # 强制让Django 添加一个描述器给反向的关联关系，
                           # 以使得ManyToManyField 的关联关系不是对称的
                           symmetrical=False
                           )
)
