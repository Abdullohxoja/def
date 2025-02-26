from rest_framework import serializers
from rest_framework.authtoken.admin import User

from app_posts.models import PostsModel, TopicsModel , PostClapsModel , PostCommentsModel


class PostsSerializer(serializers.ModelSerializer):
    topics = serializers.PrimaryKeyRelatedField(queryset=TopicsModel.objects.all() , many=True , required=False)
    class Meta:
        model = PostsModel
        fields = '__all__'





class PostClapsSerializer(serializers.Serializer):
    slug = serializers.SlugField()

    def validate(self, attrs):
        slug = attrs.get('slug')
    

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    post = serializers.PrimaryKeyRelatedField(queryset=PostsModel.objects.all())

    class Meta:
        model = PostClapsModel
        fields = ['id', 'user', 'post']

    def __str__(self):
        return f"{self.post_id} clapped by {self.user.username}"
    


##comment 

class PostCommentsModelSerializer(serializers.ModelSerializer):
    # Serializer for the nested (child) comments
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        # Only fetch replies if the comment has children
        child_comments = obj.children.all()
        return PostCommentsModelSerializer(child_comments, many=True).data

    class Meta:
        model = PostCommentsModel
        fields = ['id', 'user', 'post', 'comment', 'parent', 'children']  # Add or remove fields as needed

    # Optionally, you can add this method to return only the relevant data for the parent comment
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Add a flag to indicate whether the comment is a parent or not
        representation['is_parent'] = not instance.parent
        return representation


class ModelSerializer:
    pass