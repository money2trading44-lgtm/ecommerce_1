from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, HttpRequest

def sitemap_xml(request):
    from django.urls import reverse
    from shop.models import Product

    urls = [
        'https://dsd-general-trading.com/',
        'https://dsd-general-trading.com/telephones/',
        'https://dsd-general-trading.com/draps/',
        'https://dsd-general-trading.com/reparation/',
    ]

    try:
        products = Product.objects.filter(is_active=True)
        for product in products:
            urls.append(f'https://dsd-general-trading.com/produit/{product.id}')
    except:
        pass

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

urlpatterns = [
    path('robots.txt', robots_txt),
    path('sitemap.xml', sitemap_xml),
    path('',include('shop.urls')),
    path('administration/', include('shop.urls_admin')),
]

# ⚠️ REMPLACEZ LA LIGNE CI-DESSOUS PAR CE BLOC :
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]