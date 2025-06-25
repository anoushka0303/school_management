from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage

class UserDataPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'per-page-data'
    valid_page_sizes = [5, 10, 15, 20, 80]
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size not in self.valid_page_sizes:
                    raise ValidationError({
                        "error" : f"invalid page size for {self.page_size_query_param}",
                    })
                return page_size
            except ValueError:
                raise ValidationError({
                    "error" : f"invalid query_param. Should be {self.page_size_query_param}"
                })
        return self.page_size
    

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        
        paginator = Paginator(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            self.page = paginator.page(page_number)
        except EmptyPage:
            self.page = paginator.page(1)
            return []
            
        return list(self.page)

    def get_paginated_response(self, data):
        return Response({
            "count" : self.page.paginator.count,
            'results' : data
        })