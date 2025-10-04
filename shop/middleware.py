from django.utils.deprecation import MiddlewareMixin
from shop.models import Order, RepairRequest


class NotificationMiddleware(MiddlewareMixin):
    """Middleware pour ajouter les compteurs de notifications au contexte"""

    def process_request(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            # Commandes en attente
            pending_orders_count = Order.objects.filter(status='PENDING').count()
            request.pending_orders_count = pending_orders_count

            # Réparations en attente
            pending_repairs_count = RepairRequest.objects.filter(status='PENDING').count()
            request.pending_repairs_count = pending_repairs_count
        else:
            request.pending_orders_count = 0
            request.pending_repairs_count = 0

        return None