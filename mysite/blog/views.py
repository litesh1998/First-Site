from django.contrib.postgres import search
from django.http import response
from django.shortcuts import get_object_or_404, render
from .models import Post, Comment
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count, query
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
# Create your views here.


def post_list(request, tag_slug=None):
    objects = Post.published.all()
    tag=None

    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        objects=objects.filter(tags__in=[tag])

    paginator = Paginator(objects, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)

    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag':tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day)
    
    comments = post.comments.filter(active=True)
    new_comment=None

    if request.method =='POST':
        comment_form=CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment=comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
    else:
        comment_form=CommentForm()

    post_tag_id=post.tags.values_list('id', flat=True)
    similar_posts=Post.published.filter(tags__in=post_tag_id).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,'comments':comments,
                        'new_comment':new_comment, 'comment_form':comment_form,
                        'similar_posts':similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            to = cd['to']
            subject = f"{cd['name']} recommends that you read {post.title}"
            comment = f"Post url:{post.get_absolute_url()}\n\n {cd['name']}'s comments are:\n{cd['comment']}"
            send_mail(subject, comment, 'pheonix.code@gmail.com', [to], fail_silently=False)
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'form': form, 'post': post, 'sent': sent})


def post_search(request):
    form =SearchForm()
    query=None
    results=[]
    if 'query' in request.GET:
        form= SearchForm(request.GET)
        if form.is_valid():
            query=form.cleaned_data['query']
            search_vector=SearchVector('title', weight='A') + \
                SearchVector('body', weight='B')
            search_query=SearchQuery(query)
            results=Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.4).order_by('-rank')
    return render(request, 'blog/post/search.html',
                    {
                        'form':form,
                        'query':query,
                        'results':results
                    })
