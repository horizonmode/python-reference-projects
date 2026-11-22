from django.urls import reverse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ForecastPagination(PageNumberPagination):
    page_size = 20

    def paginate_initial_queryset(self, queryset, request):
        """Embed page one in HTML using the same page size and links as the API."""
        assert self.page_size is not None
        self.request = request
        self.page = self.django_paginator_class(queryset, self.page_size).page(1)
        return list(self.page)

    def page_link(self, number):
        assert self.request is not None, "Paginate the queryset before building links."
        url = self.request.build_absolute_uri(reverse("forecast-list"))
        return f"{url}?page={number}"

    def get_next_link(self):
        assert self.page is not None, "Paginate the queryset before building links."
        return self.page_link(self.page.next_page_number()) if self.page.has_next() else None

    def get_previous_link(self):
        assert self.page is not None, "Paginate the queryset before building links."
        return self.page_link(self.page.previous_page_number()) if self.page.has_previous() else None

    def payload(self, data):
        assert self.page is not None, "Paginate the queryset before building a response."
        return {
            "forecasts": data, "count": self.page.paginator.count,
            "next": self.get_next_link(), "previous": self.get_previous_link(),
        }

    def get_paginated_response(self, data):
        return Response(self.payload(data))
