from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('',views.home,name ='home'),
    path('draps/',views.sheets_list,name='sheets_list'),
    path('telephones/',views.phone_list,name='phones_list'),
    path('produit/<int:product_id>',views.product_detail,name='product_detail'),
    path('reparation/',views.repair_request,name='repair_request'),
    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/modifier/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('panier/supprimer/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('commande/',views.checkout,name='checkout'),
    path('commande/confirmation/<int:order_id>/',views.order_confirmation,name='order_confirmation'),
    path('mes-commandes',views.order_history,name='order_history'),
    path('recherche/', views.search_products, name='search_products'),
    path('administration/',include('shop.urls_admin'))
]