from rest_framework.serializers import ModelSerializer, SerializerMethodField, IntegerField, CurrentUserDefault, CharField, HiddenField, SlugRelatedField, PrimaryKeyRelatedField

from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text

from wsgi.feeds.models import Feed, Post, Link, FeedLink


class CreatableSlugRelatedField(SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
        except (TypeError, ValueError):
            self.fail('invalid')


class FeedLinkSerializer(ModelSerializer):

    link = CreatableSlugRelatedField(queryset=Link.objects, slug_field="url")
    feed = PrimaryKeyRelatedField(queryset=Feed.objects)

    class Meta:
        model = FeedLink
        exclude = ("id", "feed",)


class LinkSerializer(ModelSerializer):

    class Meta:
        model = Link

    def create(self, validated_data):
        item, _ = Link.objects.get_or_create(validated_data)
        return item


class FeedSerializer(ModelSerializer):
    links = FeedLinkSerializer(many=True, read_only=True)
    count = SerializerMethodField()
    position = IntegerField(read_only=True)
    user = HiddenField(default=CurrentUserDefault())
    favIcon = CharField(default='undefined', required=False)

    class Meta:
        model = Feed

    def create(self, validated_data):
        position = len(Feed.objects.filter(user=validated_data['user']))
        validated_data['position'] = position
        feed = super().create(validated_data)
        link_serializer = LinkSerializer(data=self.initial_data)
        link_serializer.is_valid()
        link = link_serializer.save()

        feedlink_serializer = FeedLinkSerializer(data={'feed': feed.pk,
                                                       'link': link,
                                                       'reg_exp': self.initial_data.get('regExp', '')})
        feedlink_serializer.is_valid()
        feedlink_serializer.save()
        return feed

    def get_count(self, obj):
        return len(Post.objects.filter(feed=obj, view=False))


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
