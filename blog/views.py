from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Blog
from .models import BlogType
from read_statistics.utils import read_statistics_once_read

each_page_blogs_num = 4


def get_blog_list_common_data(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, each_page_blogs_num)  # 每十页进行分页
    page_num = request.GET.get('page', 1)  # 获取url页码参数  get请求 如果没有给默认值1
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number  # 获取当前页码
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
        list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 加上首页和最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    #     日期分类
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')

    '''获取日期归档对应的博客数量'''
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    blog_types = BlogType.objects.annotate(blog_count=Count('blog'))
    data = {
        'blogs': page_of_blogs.object_list,
        'blog_types': blog_types,
        'page_of_blogs': page_of_blogs,
        'page_range': page_range,
        'blog_dates': blog_dates_dict,
    }
    return data


def blog_list(request):
    blogs_all_list = Blog.objects.all()
    data = get_blog_list_common_data(request, blogs_all_list)
    return render(request, 'blog/blog_list.html', context=data)


def blogs_with_type(request, blog_type_pk):
    blog_type = BlogType.objects.get(pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)

    data = get_blog_list_common_data(request, blogs_all_list)
    data['blog_type'] = blog_type

    return render(request, 'blog/blogs_with_type.html', context=data)


def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    data = get_blog_list_common_data(request, blogs_all_list)

    data['blogs_with_date'] = '%s年%s月' % (year, month)

    return render(request, 'blog/blogs_with_date.html', context=data)


def blog_detail(request, blog_pk):
    blog = Blog.objects.get(pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)

    previous_blog = Blog.objects.filter(created_time__gt=blog.created_time).last()
    next_blog = Blog.objects.filter(created_time__lt=blog.created_time).first()

    data = {
        'blog': blog,
        'previous_blog': previous_blog,
        'next_blog': next_blog,
    }
    response = render(request, 'blog/blog_detail.html', context=data)
    response.set_cookie(read_cookie_key, 'true')  # 阅读cookie标记
    return response
