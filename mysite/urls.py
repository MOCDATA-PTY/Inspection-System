from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from test_view import test_media_file, serve_media_file

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_to_login),  # Redirect root URL to login
    path('admin/', admin.site.urls),
    path('test-media/', test_media_file, name='test_media_file'),  # Test view
    path('', include('main.urls')),
    # Serve media files with custom view
    re_path(r'^media/(?P<path>.*)$', serve_media_file, name='serve_media'),
]
