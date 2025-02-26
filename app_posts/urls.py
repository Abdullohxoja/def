"""
/api/v1/posts/
"""

from django.urls import path

from app_posts.views import posts_view, posts_detail_view ,  PostCreateAPIView

app_name = 'posts'

urlpatterns = [
    path('<slug:slug>', posts_detail_view(), name='detail') ,
    path('', PostCreateAPIView.as_view(), name='list')
    path('claps', PostCreateAPIView.as_view(), name='claps')

]

