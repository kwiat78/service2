from django.contrib import admin


from wsgi.feeds.models import Feed,Link,Post, FeedLink


class FeedLinkInline(admin.TabularInline):
    model = FeedLink
    extra = 1


class FeedAdmin(admin.ModelAdmin):
    inlines = (FeedLinkInline,)
    list_display = ("__str__", 'position',)


class PostAdmin(admin.ModelAdmin):
    list_display = ("__str__","post_date","add_date")


admin.site.register(Feed, FeedAdmin)
admin.site.register(Link)
admin.site.register(Post, PostAdmin)


admin.site.register(FeedLink)
