from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from shop.models import Order, RepairRequest
from django.core.cache import cache

class NotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            cache_key_orders = f"pending_orders_{request.user.id}"
            cache_key_repairs = f"pending_repairs_{request.user.id}"

            request.pending_orders_count = cache.get_or_set(
                cache_key_orders,
                lambda: Order.objects.filter(status='PENDING').count(),
                300  # 5 minutes cache
            )
            request.pending_repairs_count = cache.get_or_set(
                cache_key_repairs,
                lambda: RepairRequest.objects.filter(status='PENDING').count(),
                300
            )
        else:
            request.pending_orders_count = 0
            request.pending_repairs_count = 0


class AdminSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # LAISSER PASSER TOUTES LES REQUÊTES pour le moment
        # On va gérer la sécurité uniquement avec les décorateurs dans les vues
        return self.get_response(request)

