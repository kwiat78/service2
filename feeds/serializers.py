from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField

from feeds.models import Feed, Post, Link, FeedLink



class FeedLinkSerializer(ModelSerializer):

    link = StringRelatedField()


    class Meta:
        model = FeedLink
        exclude = ("id","feed",)


class LinkSerializer(ModelSerializer):

    class Meta:
        model = Link

class FeedSerializer(ModelSerializer):

    links = FeedLinkSerializer(many=True)#StringRelatedField(many=True, read_only=True)
    count = SerializerMethodField()

    class Meta:
        model = Feed
        exclude = ("id",)

    def get_count(self, obj):
        return len(Post.objects.filter(feed=obj,view=False));

class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        exclude = ("id",)




