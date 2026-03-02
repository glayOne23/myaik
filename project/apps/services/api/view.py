from rest_framework.generics import(
    ListAPIView,
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView
)
from .response import custom_response_create, custom_response_retrieve, custom_response_update


class CustomListAPIView(ListAPIView):
    pass


class CustomCreateAPIView(CreateAPIView):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return custom_response_create(response)


class CustomRetrieveAPIView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return custom_response_retrieve(response)


class CustomListCreateAPIView(ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return custom_response_create(response)


class CustomRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return custom_response_retrieve(response)


class CustomRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return custom_response_retrieve(response)

    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return custom_response_update(response)

    def patch(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return custom_response_update(response)


class CustomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return custom_response_retrieve(response)

    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return custom_response_update(response)

    def patch(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return custom_response_update(response)