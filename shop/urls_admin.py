from django.urls import path

from . import views
from .views import admin_order_detail, admin_order_confirm, admin_order_update_status, admin_order_cancel, \
    admin_order_export


urlpatterns = [
    # Authentification
    path('', views.admin_login, name='admin_login'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Tableau de bord et sections
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.admin_products, name='admin_products'),
    path('products/add/', views.admin_add_product, name='admin_add_product'),
    path('products/edit/<int:product_id>/',views.admin_edit_product,name='admin_edit_product'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('repairs/', views.admin_repairs, name='admin_repairs'),
    path('orders/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('orders/<int:order_id>/confirm/', admin_order_confirm, name='admin_order_confirm'),
    path('orders/<int:order_id>/update-status/', admin_order_update_status, name='admin_order_update_status'),
    path('orders/<int:order_id>/cancel/', admin_order_cancel, name='admin_order_cancel'),
    path('orders/<int:order_id>/export/', admin_order_export, name='admin_order_export'),
    path('custom-quotes/', views.admin_custom_quotes, name='admin_custom_quotes'),
    path('custom-quotes/edit/<int:quote_id>/', views.admin_edit_quote, name='admin_edit_quote'),
    # Réparations
    path('repairs/', views.admin_repairs, name='admin_repairs'),
    path('repairs/<int:repair_id>/', views.admin_repair_detail, name='admin_repair_detail'),
    path('repairs/<int:repair_id>/update-status/', views.admin_repair_update_status, name='admin_repair_update_status'),
    path('repairs/<int:repair_id>/complete/', views.admin_repair_complete, name='admin_repair_complete'),
    path('repairs/<int:repair_id>/delete/', views.admin_repair_delete, name='admin_repair_delete'),

]