from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CountPagination(PageNumberPagination):

    def paginate_queryset(self, queryset, request, view=None):
        return queryset

    def get_paginated_response(self, data):
        return Response({
            'count': len(data),
            'results': data
        })
