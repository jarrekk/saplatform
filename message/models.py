from django.db import models


# Create your models here.

class Alert(models.Model):
    # title = models.CharField(max_length=64, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    # msg_type = models.IntegerField(blank=True, null=True)  # 0:system,1:user
    to_user_id = models.IntegerField(blank=True, null=True)
    # from_user_id = models.IntegerField(blank=True, null=True)  # 0:system
    # status = models.IntegerField(blank=True, null=True)  # 0:unread,1:read
    gen_time = models.DateTimeField(auto_now_add=True)
