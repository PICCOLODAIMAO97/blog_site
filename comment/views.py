from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm


def update_comment(request):
    comment_form = CommentForm(request.POST, user=request.user)

    if comment_form.is_valid():
        # 检查通过 保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if parent is not None:
            comment.root = parent.root if parent.root is not None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 返回数据
        username = comment.user.get_nickname_or_username()
        comment_time = comment.comment_time.strftime('%Y-%m-%d %H:%M:%S')
        content_type = ContentType.objects.get_for_model(comment).model
        text = comment.text
        data = {
            'status': 'SUCCESS',
            'username': username,
            'comment_time': comment_time,
            'text': text,
            'content_type': content_type,
        }
        if parent is not None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if comment.root is not None else ''
    else:
        data = {
            'status': 'ERROR',
            'message': list(comment_form.errors.values())[0][0],
        }
    return JsonResponse(data)
