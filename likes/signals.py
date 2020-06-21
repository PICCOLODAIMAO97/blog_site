from django.utils.html import strip_tags
from notifications.signals import notify
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LikeRecord


# 信号调度，接收点赞保存的消息
@receiver(post_save, sender=LikeRecord)
def send_notification(sender, instance, **kwargs):
    if instance.content_type.model == 'blog':
        blog = instance.content_object
        verb = '{0}点赞了你的博客《{1}》'.format(instance.user.get_nickname_or_username(), blog.title)
    elif instance.content_type.model == 'comment':
        comment = instance.content_object
        verb = '{0}点赞了你的评论"{1}"'.format(instance.user.get_nickname_or_username(), strip_tags(comment.text))

    recipient = instance.content_object.get_user()
    url = instance.content_object.get_url()
    notify.send(instance.user, recipient=recipient, verb=verb, action_object=instance, url=url)


