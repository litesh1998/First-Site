from django.http import response
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.
def post_list(request):
    objects=Post.published.all()
    paginator = Paginator(objects, 3)
    page=request.GET.get('page')

    try:
        posts=paginator.page(page)
    
    except PageNotAnInteger:
        posts=paginator.page(1)
    except EmptyPage:
        posts=paginator.page(paginator.num_pages)
    
    return render(request, 'blog/post/list.html', {'page': page, 'posts':posts})


def post_detail(request, year, month, day, post):
    post=get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {'post':post})