from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from app_common.models import BaseModel

User = get_user_model()

class TopicsModel(BaseModel):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "topic"
        verbose_name_plural = "topics"


class PostsModel(BaseModel):
    image = models.ImageField(upload_to='posts')
    author = models.ForeignKey(User , on_delete=models.CASCADE , related_name='posts')
    slug = models.SlugField(unique=True,null=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    short_description = models.CharField(max_length=255)
    topics = models.ManyToManyField(TopicsModel , related_name='posts')

    def __str__(self):
        return self.title


    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"





class PostClapsModel(BaseModel):
    user = models.ForeignKey(User , on_delete=models.SET_NULL , related_name='post_claps', null=True)
    post = models.ForeignKey(PostsModel , on_delete=models.CASCADE , related_name='claps', null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.post_id = None

    def __str__(self):
        return f"{self.post_id} clapped by {self.user.username}"



    class Meta:
        verbose_name = "post clap"
        verbose_name_plural = "post claps"



class PostCommentsModel(BaseModel):
    user = models.ForeignKey(User , on_delete=models.SET_NULL , related_name='post_comments', null=True)
    post = models.ForeignKey(PostsModel , on_delete=models.CASCADE , related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children')


    def __str__(self):
        return f"{self.user.username} commented on {self.post.id} like {self.comment}"

    class Meta:
        verbose_name = "post comment"
        verbose_name_plural = "post comments"




class PostCommentClapModel(BaseModel):
    user = models.ForeignKey(User , on_delete=models.SET_NULL , related_name='post_comments_claps', null=True)
    comment = models.ForeignKey(PostCommentsModel , on_delete=models.CASCADE , related_name='claps', null=True)


    def __str__(self):
        return f"{self.comment.id} clapped by {self.user.username}"



    class Meta:
        verbose_name = "post comment clap"
        verbose_name_plural = "post comment claps"










