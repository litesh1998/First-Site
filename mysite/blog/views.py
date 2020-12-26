from django.http import response
from django.shortcuts import get_object_or_404, render
from .models import Post, Comment
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
# Create your views here.


def post_list(request):
    objects = Post.published.all()
    paginator = Paginator(objects, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)

    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})


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

    return render(request, 'blog/post/detail.html', {'post': post,'comments':comments,'new_comment':new_comment, 'comment_form':comment_form})


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
            send_mail(subject, comment, 'admin@liteshgarg.com', [to])
            sent = True
    else:
        form = EmailPostForm

    return render(request, 'blog/post/share.html', {'form': form, 'post': post, 'sent': sent})
