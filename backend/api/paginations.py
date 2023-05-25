from rest_framework.pagination import PageNumberPagination


class PageNumberPaginationLimit(PageNumberPagination):
    """Нумерация страниц"""
    page_size = 6
    page_size_query_param = 'limit'
