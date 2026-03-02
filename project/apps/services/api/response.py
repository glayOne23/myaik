from django.conf import settings
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import status
from urllib.parse import urlparse, urlunparse


class CustomPagination(LimitOffsetPagination):
    default_limit = 12
    max_limit = 100

    def get_next_link(self):
        next_link = super().get_next_link()
        if next_link:            
            parsed_url = urlparse(next_link)
            modified_url = parsed_url._replace(netloc=settings.HOSTNAME_OVERRIDE)
            next_link = urlunparse(modified_url)
        return next_link

    def get_previous_link(self):
        previous_link = super().get_previous_link()
        if previous_link:            
            parsed_url = urlparse(previous_link)
            modified_url = parsed_url._replace(netloc=settings.HOSTNAME_OVERRIDE)
            previous_link = urlunparse(modified_url)
        return previous_link

    def get_paginated_response(self, data):        
        return Response({
            "status_code": status.HTTP_200_OK,
            "count": self.count,
            "message": "Data berhasil ditampilkan",
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "data": data
        })
    

def custom_response_create(response):
    return Response({
        'status': status.HTTP_201_CREATED,
        'message': 'Data berhasil disimpan',
        'data': response.data
    })            

def custom_response_retrieve(response):
    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Data berhasil ditampilkan',
        'data': response.data
    })      

def custom_response_update(response):
    return Response({
        'status': status.HTTP_200_OK,
        'message': 'Data berhasil diubah',
        'data': response.data
    })       