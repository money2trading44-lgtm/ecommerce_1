from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, RepairRequest, Cart, CartItem, Order, CustomQuoteRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','description']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'product_type', 'electronics_category', 'decoration_type', 'needs_custom_quote', 'on_sale', 'stock']
    list_filter = ['category', 'product_type', 'electronics_category', 'decoration_type', 'needs_custom_quote','on_sale']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'price', 'category', 'product_type', 'stock', 'image')
        }),
        ('Promotions', {
            'fields': ('on_sale', 'discount_percentage'),
            'classes': ('collapse',)
        }),
        ('Décoration & Aménagement', {  # NOUVEAU FIELDSET
            'fields': ('decoration_type', 'needs_custom_quote', 'price_per_sqm'),
            'classes': ('collapse',)
        }),
        ('Spécifications Draps', {
            'fields': ('sheet_size', 'color', 'material'),
            'classes': ('collapse',)
        }),
        ('Spécifications Électronique', {
            'fields': ('phone_brand', 'electronics_category', 'storage', 'screen_size',
                       'processor', 'ram', 'camera', 'battery', 'operating_system', 'connectivity'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active', 'created_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at']

@admin.register(RepairRequest)
class RepairRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name','device_model','issue_type','status','created_at']
    list_filter = ['issue_type','status','created_at']
    search_fields = ['full_name','device_model','phone_number']
    readonly_fields = ['created_at','updated_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'get_total_quantity', 'get_total_price', 'created_at']
    list_filter = ['created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'get_total_price']
    list_filter = ['added_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone_number', 'total_price', 'created_at', 'contact_actions']
    list_filter = ['created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

    def contact_actions(self, obj):
        """Affiche les actions de contact rapide"""
        return format_html(
            '<a href="mailto:{}" style="background: #4F46E5; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; margin-right: 8px;">📧 Email</a>'
            '<a href="https://wa.me/{}?text=Bonjour%20{},%20nous%20avons%20reçu%20votre%20commande%20{}" style="background: #25D366; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">💬 WhatsApp</a>',
            obj.email,
            obj.phone_number.replace(' ', '').replace('+', ''),
            obj.full_name.split()[0],  # Prénom seulement
            obj.order_number
        )

    contact_actions.short_description = 'Actions de contact'
    contact_actions.allow_tags = True


@admin.register(CustomQuoteRequest)  # NOUVEAU
class CustomQuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['product', 'full_name', 'phone_number', 'city', 'preferred_date', 'status', 'created_at']
    list_filter = ['status', 'product__decoration_type', 'preferred_date', 'created_at']
    search_fields = ['full_name', 'phone_number', 'email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']

    fieldsets = (
        ('Informations client', {
            'fields': ('full_name', 'phone_number', 'email', 'address', 'city')
        }),
        ('Rendez-vous', {
            'fields': ('preferred_date', 'preferred_time')
        }),
        ('Informations pour le devis', {
            'fields': ('room_dimensions', 'window_measurements', 'bed_size',
                       'fabric_preference', 'color_preferences', 'special_requests')
        }),
        ('Gestion', {
            'fields': ('product', 'status', 'admin_notes', 'quoted_price')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def contact_actions(self, obj):
        """Affiche les actions de contact rapide"""
        return format_html(
            '<a href="mailto:{}" style="background: #4F46E5; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; margin-right: 8px;">📧 Email</a>'
            '<a href="https://wa.me/{}?text=Bonjour%20{},%20concernant%20votre%20demande%20de%20devis%20pour%20{}" style="background: #25D366; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none;">💬 WhatsApp</a>',
            obj.email,
            obj.phone_number.replace(' ', '').replace('+', ''),
            obj.full_name.split()[0],
            obj.product.name
        )

    contact_actions.short_description = 'Actions de contact'
    contact_actions.allow_tags = True