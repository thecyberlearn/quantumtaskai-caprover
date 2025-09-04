from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest


def custom_404_view(request, exception):
    """Custom 404 error page with agent theme"""
    return HttpResponseNotFound(
        render(request, '404.html', {
            'timestamp': '1.0'  # Cache busting for CSS
        }).content
    )


def custom_500_view(request):
    """Custom 500 error page with agent theme"""
    return HttpResponseServerError(
        render(request, '500.html', {
            'timestamp': '1.0'  # Cache busting for CSS
        }).content
    )


def custom_403_view(request, exception):
    """Custom 403 error page with agent theme"""
    return HttpResponseForbidden(
        render(request, '403.html', {
            'timestamp': '1.0'  # Cache busting for CSS
        }).content
    )


def custom_400_view(request, exception):
    """Custom 400 error page with agent theme"""
    return HttpResponseBadRequest(
        render(request, '400.html', {
            'timestamp': '1.0'  # Cache busting for CSS
        }).content
    )