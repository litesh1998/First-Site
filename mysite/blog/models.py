from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.utils import timezone



class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')

class Post(models.Model):

    STATUS_CHOICES=(('draft', 'DRAFT'), ('published', 'Published'))

    title=models.CharField(max_length=250)
    slug=models.SlugField(unique_for_date='publish')
    author=models.ForeignKey(User, on_delete=CASCADE, related_name='blog_posts')
    publish=models.DateTimeField(default=timezone.now)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    body=models.TextField()
    status=models.CharField(max_length=25, choices=STATUS_CHOICES, default='draft')


    objects=models.Manager()
    published=PublishedManager()

    class Meta:
        ordering = ('-publish',)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year,
            self.publish.month, self.publish.day,self.slug])
