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
from shop.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap

from django.http import HttpResponse, HttpRequest


def sitemap_xml(request):
    from django.urls import reverse
    from shop.models import Product

    # URLs statiques
    urls = [
        'https://dsd-general-trading.com/',
        'https://dsd-general-trading.com/telephones/',
        'https://dsd-general-trading.com/draps/',
        'https://dsd-general-trading.com/reparation/',
    ]

    # Ajouter les produits
    try:
        products = Product.objects.filter(is_active=True)
        for product in products:
            urls.append(f'https://dsd-general-trading.com/produit/{product.id}')
    except:
        pass  # En cas d'erreur DB, on garde les URLs statiques

    # Générer le XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:
        xml_content += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'

    xml_content += '</urlset>'

    return HttpResponse(xml_content, content_type='application/xml')

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Pour la production, on sert aussi les médias
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
