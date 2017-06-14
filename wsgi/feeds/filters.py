from datetime import datetime

from rest_framework.filters import BaseFilterBackend

from wsgi.feeds.models import Post


VIEW_CRITERION = {"True": False, "False": True}
MENTIONED_CRITERION = {"True": True, "False": False}


class PostFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        criteria = {}

        if "name" in request.query_params:
            criteria["feed__id"] = request.query_params.get("name")

        if "new" in request.query_params:
            criterion = request.query_params.get("new").capitalize()
            if criterion in VIEW_CRITERION:
                criteria["view"] = VIEW_CRITERION[criterion]

        if "mentioned" in request.query_params:
            criterion = request.query_params.get("mentioned").capitalize()
            if criterion in MENTIONED_CRITERION:
                criteria["mentioned"] = MENTIONED_CRITERION[criterion]

        if "current" in request.query_params:
            current = datetime.fromtimestamp(float(request.query_params.get("current")))
            criteria["add_date__gte"] = current
            criteria["add_date__lte"] = datetime.now()

        return Post.objects.filter(feed__user=request.user, **criteria).order_by("-post_date")
