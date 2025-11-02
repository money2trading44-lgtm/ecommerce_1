from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('',views.home,name ='home'),
    path('deco-amenagement/', views.decoration_list, name='decoration_list'),
    path('electronique-accessoires/', views.electronics_list, name='electronics_list'),
    path('produit/<int:product_id>',views.product_detail,name='product_detail'),
    path('reparation/',views.repair_request,name='repair_request'),
    path('devis-personnalise/<int:product_id>/', views.custom_quote_request, name='custom_quote_request'),
    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('panier/modifier/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('panier/supprimer/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('commande/',views.checkout,name='checkout'),
    path('commande/confirmation/<int:order_id>/',views.order_confirmation,name='order_confirmation'),

    # Paiement
    path('commande/paiement/<int:order_id>/', views.process_payment, name='process_payment'),
    path('commande/annulation/<int:order_id>/', views.payment_cancel, name='payment_cancel'),
    path('commande/echec-paiement/<int:order_id>/', views.payment_failed, name='payment_failed'),
    path('devis/confirmation/<int:quote_id>/', views.quote_confirmation, name='quote_confirmation'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    path('mes-commandes',views.order_history,name='order_history'),
    path('recherche/', views.search_products, name='search_products'),
    path('gestion-securisee/',include('shop.urls_admin')),
    path('administration/',views.admin_redirect,name='admin_redirect'),
]