from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage

class UserDataPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page-size'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size < 1:
                    return 0  
                return page_size
            except ValueError:
                return 0
        return self.page_size

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if page_size == 0:
            self.page_size_actual = 0
            self.page_number_actual = request.query_params.get(self.page_query_param, 1)
            return []

        self.page_size_actual = page_size

        paginator = Paginator(queryset, page_size)

        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            page_number = int(page_number)
            if page_number < 1:
                self.page_number_actual = page_number
                return [] 
        except ValueError:
            self.page_number_actual = page_number
            return [] 

        self.page_number_actual = page_number

        try:
            self.page = paginator.page(page_number)
        except EmptyPage:
            return [] 

        return list(self.page)

    def get_paginated_response(self, data):
        count = self.page.paginator.count if hasattr(self, 'page') and self.page_size_actual else 0
        if int(self.page_number_actual) < 1 or int(self.page_size_actual) < 1:
            return Response({
                "has_error" : True,
                "error" : "page size of page number cannot be less than 1"
            })
        else:
            return Response({
                "count": count,
                "page": self.page_number_actual,
                "page_size": self.page_size_actual,
                "results": data
            })