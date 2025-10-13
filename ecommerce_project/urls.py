"""
URL configuration for ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from shop.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap

from django.http import HttpResponse, HttpRequest


def sitemap_xml(request: HttpRequest):
    from django.contrib.sitemaps.views import sitemap as sitemap_view
    return sitemap_view(request, sitemaps=sitemaps)

def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /gestion-securisee/

Sitemap: https://dsd-general-trading.com/sitemap.xml"""
    return HttpResponse(content, content_type="text/plain")

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('',include('shop.urls')),
    path('administration/', include('shop.urls_admin')),
    # SEO URLs


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
