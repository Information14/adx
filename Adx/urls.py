"""
URL configuration for Adx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views
    1. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function:  from other_app import views
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'Project/',
        include("django.contrib.auth.urls")
    ),

    path(
        '',
        include("Project.urls")
    ),

]


urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT
)


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)