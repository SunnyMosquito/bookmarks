from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.
class Action(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE,
                            db_index=True)
    # 这是用户执行操作的动作描述
    verb = models.CharField(max_length=255)
    target_ct = models.ForeignKey(ContentType,
                                  on_delete=models.CASCADE,
                                  blank=True,
                                  null=True,
                                  related_name='target_obj')
    target_id = models.PositiveIntegerField(null=True,
                                            blank=True,
                                            db_index=True)
    target = GenericForeignKey('target_ct', 'target_id')
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)
    
    class Meta:
        ordering = ('-created',)
