import datetime
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Q
from django.core.cache import cache
from django.core.paginator import Paginator
from read_statistics.utils import get_seven_days_read_data
from read_statistics.utils import get_today_hot_data
from read_statistics.utils import get_yesterday_hot_data
from blog.models import Blog


def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date) \
        .values('id', 'title') \
        .annotate(read_num_sum=Sum('read_details__read_num')) \
        .order_by('-read_num_sum')
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates_list, read_nums_list = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    # 获取七天热门博客的缓存数据
    hot_blogs_for_7_days = cache.get('hot_blogs_for_7_days')
    if hot_blogs_for_7_days is None:
        hot_blogs_for_7_days = get_7_days_hot_blogs()
        cache.set('hot_blogs_for_7_days', hot_blogs_for_7_days, 3600)

    data = {
        'read_nums_list': read_nums_list,
        'dates_list': dates_list,
        'today_hot_data': today_hot_data,
        'yesterday_hot_data': yesterday_hot_data,
        'hot_blogs_for_7_days': hot_blogs_for_7_days,
    }
    return render(request, 'home.html', context=data)


def search(request):
    search_words = request.GET.get('wd', '').strip()
    # 分词：按空格 & | ~
    condition = None
    for word in search_words.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)
    search_blogs = []
    if condition is not None:
        # 筛选：搜索
        search_blogs = Blog.objects.filter(condition)

    # 分页
    paginator = Paginator(search_blogs, 20)
    page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    search_blogs_count = search_blogs.count()

    data = {
        'search_words': search_words,
        'search_blogs_count': search_blogs_count,
        'page_of_blogs': page_of_blogs,
    }
    return render(request, 'search.html', context=data)


