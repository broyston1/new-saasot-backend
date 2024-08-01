from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# class FiveRecordsPagination(PageNumberPagination):
#     page_size = 6
#     page_size_query_param = 'page'
#     max_page_size = 6
class CustomPagination(PageNumberPagination):
    # page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50
    # page_query_param = 'p'

    def get_page_size(self, request):
        if request.query_params.get('page') == '1':
            return 20  # First page contains 20 elements
        else:
            return 20
    
    # def get_paginated_response(self, data):
    #     return Response({
    #         'links': {
    #             'next': self.get_next_link(),
    #             'previous': self.get_previous_link()
    #         },
    #         'count': self.page.paginator.count,
    #         'data': data
    #     })

    def get_previous_link(self):
        if self.page.number > 1:
            url = self.request.build_absolute_uri()
            page_number = self.page.number - 1
            return url.replace(f'page={self.page.number}', f'page={page_number}')
        return None
