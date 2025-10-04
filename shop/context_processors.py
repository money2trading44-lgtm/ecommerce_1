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