# shop/context_processors.py
from .models import Cart


def cart_context(request):
    """Ajoute le panier au contexte de toutes les templates"""

    def get_or_create_cart(request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    cart = get_or_create_cart(request)
    return {
        'cart': cart
    }


def admin_notifications(request):
    """Context processor pour les badges de notification dans l'admin"""
    if request.user.is_authenticated and request.user.is_staff:
        pending_orders_count = 0
        pending_quotes_count = 0
        pending_repairs_count = 0

        try:
            from .models import Order, CustomQuoteRequest, RepairRequest
            pending_orders_count = Order.objects.filter(status='PENDING').count()
            pending_quotes_count = CustomQuoteRequest.objects.filter(status='PENDING').count()
            pending_repairs_count = RepairRequest.objects.filter(status='PENDING').count()
        except:
            pass

        return {
            'pending_orders_count': pending_orders_count,
            'pending_quotes_count': pending_quotes_count,
            'pending_repairs_count': pending_repairs_count,
        }
    return {}