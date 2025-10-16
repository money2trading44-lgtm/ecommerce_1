import os

from django.db.models.functions import ExtractMonth
from django.utils import timezone as django_timezone, timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from shop.models import Category, Product, RepairRequest, Cart, CartItem, Order, OrderItem,CustomQuoteRequest
from django.db.models import Sum, Q
from datetime import timedelta, datetime
import requests
import json


# ========================= VUES CLIENT ======================

def home(request):
    categories = Category.objects.all()
    promotions = Product.objects.filter(on_sale=True, is_active=True)[:3]

    # Gestion de la recherche
    search_query = request.GET.get('search', '')
    products = Product.objects.filter(is_active=True)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )[:12]  # Limite à 12 résultats

    context = {
        'categories': categories,
        'promotions': promotions,
        'search_query': search_query,
        'search_results': products if search_query else None,
    }

    return render(request, 'shop/home.html', context)


def search_products(request):
    """Vue dediee pour la recherche des produits"""

    search_query = request.GET.get('q','')

    if search_query:
        products = Product.objects.filter(
            Q(name__icontains = search_query)|
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(phone_brand__icontains=search_query) |
            Q(material__icontains=search_query),
            is_active = True
        ).distinct()
    else:
        products = Product.objects.none()

    # Gestion des filtres
    product_type = request.GET.get('type','')
    if product_type:
        products = products.filter(product_type = product_type)

    context = {
        'search_results':products,
        'search_query':search_query,
        'product_type':product_type,
        'total_resuts':products.count()
    }

    return render(request,'shop/search_results.html',context)

def decoration_list(request):
    """
    Vue pour afficher les articles de décoration d'intérieur
    avec gestion des produits à prix personnalisé
    """
    decorations = Product.objects.filter(
        product_type='DECORATION',
        is_active=True
    )

    # Filtres spécifiques à la décoration
    decoration_type = request.GET.get('type', '')
    needs_quote = request.GET.get('needs_quote', '')

    if decoration_type:
        decorations = decorations.filter(decoration_type=decoration_type)

    if needs_quote == 'custom':
        decorations = decorations.filter(needs_custom_quote=True)
    elif needs_quote == 'standard':
        decorations = decorations.filter(needs_custom_quote=False)

    # Gestion du tri
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_asc':
        decorations = decorations.order_by('price')
    elif sort_by == 'price_desc':
        decorations = decorations.order_by('-price')
    elif sort_by == 'new':
        decorations = decorations.order_by('-created_at')
    else:
        decorations = decorations.order_by('-created_at')

    context = {
        'decorations': decorations,
        'decoration_types': [
            ('SHEET', 'Draps'),
            ('CURTAIN', 'Rideaux'),
            ('CARPET', 'Tapis'),
            ('OTHER', 'Autre'),
        ],
        'selected_type': decoration_type,
        'selected_quote_filter': needs_quote,
        'sort_by': sort_by,
    }

    return render(request, 'shop/decoration_list.html', context)

def phone_list(request):

    phones = Product.objects.filter(product_type = 'PHONE',is_active = True)

    # Filtres
    selected_brand = request.GET.get('brand','')
    selected_category = request.GET.get('category','')
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price', '')

    if selected_brand:
        phones = phones.filter(phone_brand=selected_brand)
    if selected_category:
        phones = phones.filter(phone_category=selected_category)
    if min_price:
        phones = phones.filter(price__gte=min_price)
    if max_price:
        phones = phones.filter(price__lte=max_price)

# Tri
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_asc':
        phones = phones.order_by('price')
    elif sort_by == 'price_desc':
        phones = phones.order_by('-price')
    elif sort_by == 'new':
        phones = phones.order_by('-created_at')
    else:
        phones = phones.order_by('-created_at')  # Par défaut: nouveautés

    context = {
        'phones':phones,
        'selected_brand':selected_brand,
        'selected_category':selected_category,
        'min_price':min_price,
        'max_price':max_price,
        'sort_by':sort_by,
        'phone_brands':Product.PHONE_BRANDS,
        'phone_categories':Product.PHONE_CATEGORIES
    }

    return render(request,'shop/phones_list.html',context)



def product_detail(request,product_id):

    product = get_object_or_404(Product,id =product_id,is_active = True)
    if product.needs_custom_quote:
        messages.info(request,
                      "Ce produit nécessite un devis personnalisé. Veuillez utiliser le formulaire de demande de rendez-vous.")
        return redirect('shop:custom_quote_request', product_id=product.id)
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        needs_custom_quote=False  # ✅ EXCLURE LES PRODUITS SUR DEVIS
    ).exclude(id=product_id)[:4]

    context = {
        'product':product,
        'similar_products':similar_products
    }

    return render(request,'shop/product_detail.html',context)


def repair_request(request):

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        issue_type = request.POST.get('issue_type')
        device_model = request.POST.get('device_model')
        description = request.POST.get('description')

        # Creation de la demande

        repair_request = RepairRequest(
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            issue_type=issue_type,
            device_model=device_model,
            description=description
        )
        repair_request.save()

        messages.success(request,'Votre demande de réparation a été envoyée avec succès !',extra_tags='repair')
        return redirect('shop:repair_request')
    return render(request,'shop/repair_request.html')


def custom_quote_request(request, product_id):
    """Vue pour la demande de devis personnalisé"""
    product = get_object_or_404(Product, id=product_id, needs_custom_quote=True)

    if request.method == 'POST':
        # Traitement du formulaire de demande de devis
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')

        # Informations spécifiques
        room_dimensions = request.POST.get('room_dimensions', '')
        window_measurements = request.POST.get('window_measurements', '')
        bed_size = request.POST.get('bed_size', '')
        special_requests = request.POST.get('special_requests', '')
        fabric_preference = request.POST.get('fabric_preference', '')
        color_preferences = request.POST.get('color_preferences', '')

        # Validation des champs obligatoires
        required_fields = ['full_name', 'phone_number', 'email', 'address', 'city', 'preferred_date', 'preferred_time']
        missing_fields = [field for field in required_fields if not request.POST.get(field)]

        if missing_fields:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('shop:custom_quote_request', product_id=product_id)

        try:
            # Créer la demande de devis
            quote_request = CustomQuoteRequest(
                product=product,
                full_name=full_name,
                phone_number=phone_number,
                email=email,
                address=address,
                city=city,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                room_dimensions=room_dimensions,
                window_measurements=window_measurements,
                bed_size=bed_size,
                special_requests=special_requests,
                fabric_preference=fabric_preference,
                color_preferences=color_preferences
            )
            quote_request.save()

            # Sauvegarder la demande
            quote_request = CustomQuoteRequest(
                product=product,
                full_name=full_name,
                phone_number=phone_number,
                email=email,
                address=address,
                city=city,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                room_dimensions=room_dimensions,
                window_measurements=window_measurements,
                bed_size=bed_size,
                special_requests=special_requests,
                fabric_preference=fabric_preference,
                color_preferences=color_preferences
            )
            quote_request.save()


            # Rediriger vers la page de confirmation
            return render(request, 'shop/quote_confirmation.html', {'quote_request': quote_request})

        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
            return redirect('shop:custom_quote_request', product_id=product_id)

    context = {
        'product': product,
    }
    return render(request, 'shop/custom_quote_request.html', context)

def quote_confirmation(request, quote_id):
    quote_request = get_object_or_404(CustomQuoteRequest, id=quote_id)
    return render(request, 'shop/quote_confirmation.html', {'quote_request': quote_request})

def get_or_create_cart(request):
    """
    Récupère ou crée un panier pour l'utilisateur (si connecté)
    ou pour la session (si non connecté).
    """
    if request.user.is_authenticated:
        # Panier lié à l'utilisateur connecté
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Panier lié à la session anonyme
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    return cart


def cart_detail(request):
    """
    Vue pour afficher le panier
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')

    context = {
        'cart':cart,
        'cart_items':cart_items
    }
    return render(request,'shop/cart_detail.html',context)


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # EMPÊCHER L'AJOUT AU PANIER POUR LES PRODUITS À DEVIS PERSONNALISÉ
        if product.needs_custom_quote:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Ce produit nécessite un devis personnalisé. Veuillez utiliser le formulaire de demande de rendez-vous.'
                })
            messages.info(request,
                          'Ce produit nécessite un devis personnalisé. Veuillez utiliser le formulaire de demande de rendez-vous.')
            return redirect('shop:custom_quote_request', product_id=product_id)

        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))

        # Vérification du stock
        if product.stock < quantity:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuffisant. Il ne reste que {product.stock} unité(s) disponible(s).'
                })
            messages.error(request, f'Stock insuffisant. Il ne reste que {product.stock} unité(s) disponible(s).')
            return redirect('shop:product_detail', product_id=product_id)

        # Ajouter ou mettre à jour l'article
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Recharger le panier pour avoir les données fraîches
        cart = get_or_create_cart(request)

        # Réponse AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_quantity(),
                'message': f"{product.name} ajouté au panier !"
            })

        messages.success(request, f'{product.name} ajouté au panier !')
        return redirect('shop:cart_detail')

    return redirect('shop:product_detail', product_id=product_id)


def update_cart_item(request, item_id):
    """Vue pour mettre à jour la quantité d'un article avec support AJAX"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
            message = "Article supprimé du panier."
            deleted = True
        else:
            if cart_item.product.stock < quantity:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f"Stock insuffisant. Il ne reste que {cart_item.product.stock} unité(s) disponible(s)."
                    })
                messages.error(request,
                               f"Stock insuffisant. Il ne reste que {cart_item.product.stock} unité(s) disponible(s).")
                return redirect('shop:cart_detail')

            cart_item.quantity = quantity
            cart_item.save()
            message = "Quantité mise à jour."
            deleted = False

        # Réponse pour AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = get_or_create_cart(request)  # Recharger le panier
            return JsonResponse({
                'success': True,
                'message': message,
                'deleted': deleted,
                'item_total': float(cart_item.get_total_price()) if not deleted else 0,
                'cart_total': float(cart.get_total_price()),
                'cart_quantity': cart.get_total_quantity(),
                'item_quantity': quantity if not deleted else 0
            })

        messages.success(request, message)
        return redirect('shop:cart_detail')

    return redirect('shop:cart_detail')


def remove_from_cart(request, item_id):
    """Vue pour supprimer un article du panier avec support AJAX"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()

        # Réponse pour AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = get_or_create_cart(request)  # Recharger le panier
            return JsonResponse({
                'success': True,
                'message': f"{product_name} supprimé du panier.",
                'deleted': True,
                'cart_total': float(cart.get_total_price()),
                'cart_quantity': cart.get_total_quantity()
            })

        messages.success(request, f"{product_name} supprimé du panier.")
        return redirect('shop:cart_detail')

    return redirect('shop:cart_detail')


def process_payment(request, order_id):
    """
    Vue pour traiter le paiement en ligne via PayDunya
    """
    print("🎯 PROCESS_PAYMENT appelée")  # DEBUG
    order = get_object_or_404(Order, id=order_id)
    print(f"🎯 Commande #{order.order_number} - Méthode: {order.payment_method}")

    # Si paiement à la livraison, rediriger directement vers confirmation
    if order.payment_method == 'CASH':
        print("🎯 Paiement cash - redirection confirmation")
        return redirect('shop:order_confirmation', order_id=order.id)

    # Configuration PayDunya
    PAYDUNYA_CONFIG = {
        'MASTER_KEY': os.environ.get('PAYDUNYA_MASTER_KEY', ''),
        'PRIVATE_KEY': os.environ.get('PAYDUNYA_PRIVATE_KEY', ''),
        'PUBLIC_KEY': os.environ.get('PAYDUNYA_PUBLIC_KEY', ''),
        'TOKEN': os.environ.get('PAYDUNYA_TOKEN', ''),
        'MODE': 'test'  # Mettre 'live' en production
    }
    print(f"🎯 Clés configurées: {bool(PAYDUNYA_CONFIG['MASTER_KEY'])}")  # DEBUG

    if not all([PAYDUNYA_CONFIG['MASTER_KEY'], PAYDUNYA_CONFIG['PRIVATE_KEY'],
                PAYDUNYA_CONFIG['PUBLIC_KEY'], PAYDUNYA_CONFIG['TOKEN']]):
        print("❌ Clés manquantes")
        messages.error(request, "Configuration de paiement incomplète. Veuillez réessayer plus tard.")
        return redirect('shop:checkout')

    try:
        print("🎯 Tentative de création de facture PayDunya...")

        # Préparer les données pour PayDunya
        store = {
            "name": "DSD General Trading",
            "tagline": "Confort & Technologie Réunis",
            "postal_address": "Abidjan, Côte d'Ivoire",
            "phone_number": "+2250102030405",
            "website_url": "https://dsd-general-trading.com",
            "logo_url": "https://dsd-general-trading.com/static/shop/images/logo.jpg"
        }

        items = []
        for item in order.items.all():
            items.append({
                "name": item.product_name,
                "quantity": item.quantity,
                "unit_price": str(float(item.product_price)),
                "total_price": str(float(item.get_total_price())),
                "description": f"{item.product_name} - {order.get_payment_method_display()}"
            })

        # Données de la requête PayDunya
        payload = {
            "invoice": {
                "items": items,
                "total_amount": str(float(order.total_price)),
                "description": f"Commande #{order.order_number}"
            },
            "store": store,
            "custom_data": {
                "order_id": order.id,
                "order_number": order.order_number
            },
            "actions": {
                "cancel_url": f"https://dsd-general-trading.com/commande/annulation/{order.id}/",
                "return_url": f"https://dsd-general-trading.com/commande/confirmation/{order.id}/",
                "callback_url": f"https://dsd-general-trading.com/payment/webhook/"
            }
        }

        # Headers pour l'API PayDunya
        headers = {
            "PAYDUNYA-MASTER-KEY": PAYDUNYA_CONFIG['MASTER_KEY'],
            "PAYDUNYA-PRIVATE-KEY": PAYDUNYA_CONFIG['PRIVATE_KEY'],
            "PAYDUNYA-PUBLIC-KEY": PAYDUNYA_CONFIG['PUBLIC_KEY'],
            "PAYDUNYA-TOKEN": PAYDUNYA_CONFIG['TOKEN'],
            "Content-Type": "application/json"
        }

        # Envoyer la requête à PayDunya (mode test)
        print("🎯 Envoi requête à PayDunya...")
        if PAYDUNYA_CONFIG['MODE'] == 'test':
            response = requests.post(
                "https://app.paydunya.com/api/v1/checkout-invoice/create",
                json=payload,
                headers=headers,
                timeout=30
            )
        else:
            response = requests.post(
                "https://app.paydunya.com/api/v1/checkout-invoice/create",
                json=payload,
                headers=headers,
                timeout=30
            )

        # 🔥🔥🔥 DEBUG COMPLET 🔥🔥🔥
        print(f"🎯 Statut HTTP: {response.status_code}")
        print(f"🎯 Réponse PayDunya: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"🎯 Données reçues: {data}")

            if data.get('response_code') == '00':  # Succès
                print("✅ Succès PayDunya - Redirection...")
                order.payment_reference = data['token']
                order.save()
                return redirect(data['response_text'])
            else:
                print(f"❌ Erreur PayDunya: {data}")
                messages.error(request, f"Erreur de paiement: {data.get('response_text', 'Erreur inconnue')}")
                return redirect('shop:checkout')

        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            messages.error(request, "Erreur de connexion avec le service de paiement")
            return redirect('shop:checkout')

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        messages.error(request, f"Erreur lors du traitement du paiement: {str(e)}")
        return redirect('shop:checkout')

def payment_webhook(request):
    """Webhook pour recevoir les confirmations de paiement de PayDunya"""

    if request.method =='POST':
        try:
            data = json.loads(request.body)
            # Vérifier la signature PayDunya
            # (à implémenter avec vos clés)

            order_id = data.get('custom_data', {}).get('order_id')
            status = data.get('status')

            if order_id and status:
                order = Order.objects.get(id=order_id)

                if status == 'completed':
                    order.payment_status = 'PAID'
                    order.status = 'CONFIRMED'  # Confirmer la commande
                    messages.success(request, f"Paiement confirmé pour la commande #{order.order_number}")
                else:
                    order.payment_status = 'FAILED'
                    messages.error(request, f"Paiement échoué pour la commande #{order.order_number}")

                order.save()

            return HttpResponse(status=200)

        except Exception as e:
            print(f"Erreur webhook: {str(e)}")
            return HttpResponse(status=400)

    return HttpResponse(status=405)


def payment_cancel(request, order_id):
    """
    Vue appelée quand l'utilisateur annule le paiement
    """
    order = get_object_or_404(Order, id=order_id)

    # Marquer le paiement comme annulé
    order.payment_status = 'FAILED'
    order.save()

    messages.warning(request, f"Paiement annulé pour la commande #{order.order_number}")
    return redirect('shop:checkout')


def checkout(request):
    """
    Vue pour la page de commande AVEC PAIEMENTS
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product')

    if not cart_items:
        messages.error(request, "Votre panier est vide.")
        return redirect('shop:cart_detail')

    # Vérifier le stock
    for item in cart_items:
        if item.quantity > item.product.stock:
            messages.error(request,
                           f"Stock insuffisant pour {item.product.name}. Il ne reste que {item.product.stock} unité(s) disponible(s).")
            return redirect('shop:cart_detail')

    if request.method == 'POST':
        # Récupérer la méthode de paiement
        payment_method = request.POST.get('payment_method', 'CASH')

        # Données client
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country', 'Côte d\'Ivoire')

        # Validation
        if not all([full_name, email, phone_number, address, city]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('shop:checkout')

        # Créer la commande
        order = Order(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            address=address,
            city=city,
            country=country,
            total_price=cart.get_total_price(),
            session_key=request.session.session_key if not request.user.is_authenticated else None,
            payment_method=payment_method,
            payment_status='CASH_ON_DELIVERY' if payment_method == 'CASH' else 'PENDING'
        )
        order.save()

        # Créer les OrderItems
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.get_discounted_price() if cart_item.product.on_sale else cart_item.product.price,
                quantity=cart_item.quantity
            )
            order_item.save()

            # Mettre à jour les stocks IMMÉDIATEMENT
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # 🔥 CORRECTION : Vider le panier SEULEMENT pour paiement à la livraison
        if payment_method == 'CASH':
            cart.items.all().delete()
            messages.success(request,
                             f"Votre commande #{order.order_number} a été passée avec succès ! Paiement à la livraison.")
            return redirect('shop:order_confirmation', order_id=order.id)
        else:
            # 🔥 CORRECTION : NE PAS VIDER LE PANIER pour paiements en ligne
            # Le panier sera vidé après confirmation du paiement
            return redirect('shop:process_payment', order_id=order.id)

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/checkout.html', context)


def order_confirmation(request, order_id):
    """
    Vue pour la page de confirmation de commande
    """
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
    }

    return render(request, 'shop/order_confirmation.html', context)


def order_history(request):
    """
    Vue pour afficher l'historique des commandes
    """
    orders = Order.objects.none()  # QuerySet vide par défaut

    if request.user.is_authenticated:
        # Pour les utilisateurs connectés : filtrer par email
        orders = Order.objects.filter(
            email=request.user.email
        ).prefetch_related('items').order_by('-created_at')

    elif request.session.session_key:
        # Pour les utilisateurs non connectés : filtrer par session_key
        orders = Order.objects.filter(
            session_key=request.session.session_key
        ).prefetch_related('items').order_by('-created_at')

    else:
        # Aucune session, afficher un message
        messages.info(request,
                      "Votre historique de commandes n'est pas disponible. Passez une commande ou connectez-vous.")

    context = {
        'orders': orders,
    }

    return render(request, 'shop/order_history.html', context)


    # ========================= VUES ADMINISTRATION ======================

# ========================= VUES ADMINISTRATEUR ======================

    """
    Ici est decrit toute la logique de la partie administrateur du site internet.
    """

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('shop:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def admin_redirect(request):
    """Redirige les accès non autorisés vers l'accueil"""
    # UN SEUL message au lieu de plusieurs
    messages.error(request, "Accès réservé aux administrateurs.")
    return redirect('shop:home')

def is_admin_user(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_authenticated and user.is_staff



def admin_login(request):
    """
    Vue pour la connexion administrateur
    """

    # SI l'utilisateur est déjà connecté, rediriger vers le dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/gestion-securisee/dashboard/')

    # SI méthode POST : traiter la connexion
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('/gestion-securisee/dashboard/')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            # IMPORTANT: Utiliser notre template personnalisé
            return render(request, 'administration/login.html')

    # SI méthode GET : afficher NOTRE formulaire de login
    return render(request, 'administration/login.html')


@admin_required
def admin_logout(request):
    """Vue pour la déconnexion administrateur"""
    # Déconnecter l'utilisateur s'il est connecté
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Vous avez été déconnecté avec succès.")

    # Rediriger vers notre page de login personnalisée
    return redirect('/gestion-securisee/login/')


@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Vue du tableau de bord administrateur avec statistiques et graphique des ventes."""

    # ✅ Récupération des statistiques globales
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_repairs = RepairRequest.objects.count()

    # ✅ Récupération de l'année courante
    current_year = datetime.now().year

    # ✅ Agrégation des ventes par mois pour l'année courante
    sales_data = (
        Order.objects.filter(created_at__year=current_year)
        .annotate(month=ExtractMonth('created_at'))
        .values('month')
        .annotate(total_sales=Sum('total_price'))
        .order_by('month')
    )

    # ✅ Construction du tableau des ventes mensuelles
    monthly_sales = [0] * 12
    for entry in sales_data:
        month_index = entry['month'] - 1
        monthly_sales[month_index] = float(entry['total_sales'])

    # ✅ Statistiques sur les réparations
    repair_status_stats = (
        RepairRequest.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )
    repair_stats_dict = {r['status']: r['total'] for r in repair_status_stats}
    repairs_pending = repair_stats_dict.get('PENDING', 0)
    repairs_in_progress = repair_stats_dict.get('IN_PROGRESS', 0)
    repairs_completed = repair_stats_dict.get('COMPLETED', 0)
    repairs_cancelled = repair_stats_dict.get('CANCELLED', 0)

    recent_orders = Order.objects.order_by('-created_at')[:5]  # les 5 dernières commandes

    # ✅ Préparation du contexte
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_repairs': total_repairs,
        'sales_data': monthly_sales,
        'current_year': current_year,
        'repairs_pending': repairs_pending,
        'repairs_in_progress': repairs_in_progress,
        'repairs_completed': repairs_completed,
        'repairs_cancelled': repairs_cancelled,
        'recent_orders':recent_orders
    }

    return render(request, 'administration/dashboard.html', context)

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_products(request):
    """Vue pour la gestion des produits avec filtres"""
    # Récupérer tous les produits avec leurs catégories
    products = Product.objects.all().select_related('category')

    # === FILTRES ===
    # Filtre par type de produit
    product_type_filter = request.GET.get('product_type', '')
    if product_type_filter:
        products = products.filter(product_type=product_type_filter)

    # Filtre par catégorie
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Filtre par statut
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        products = products.filter(is_active=True)
    elif status_filter == 'inactive':
        products = products.filter(is_active=False)

    # Filtre par recherche
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Calcul des statistiques (basées sur les filtres appliqués)
    total_products = products.count()
    products_on_sale = products.filter(on_sale=True).count()
    products_out_of_stock = products.filter(stock=0).count()

    # Récupérer toutes les catégories pour le filtre
    categories = Category.objects.all()

    context = {
        'products': products,
        'total_products': total_products,
        'products_on_sale': products_on_sale,
        'products_out_of_stock': products_out_of_stock,
        'categories': categories,

        # Valeurs actuelles des filtres pour les pré-remplir
        'current_product_type': product_type_filter,
        'current_category': category_filter,
        'current_status': status_filter,
        'current_search': search_query,
    }
    return render(request, 'administration/products.html', context)



@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_orders(request):
    """Vue pour la gestion des commandes avec filtres"""
    # Récupérer toutes les commandes avec leurs articles
    orders = Order.objects.all().prefetch_related('items__product').order_by('-created_at')

    # === FILTRES ===
    # Filtre par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter.upper())

    # Filtre par période
    period_filter = request.GET.get('period', '')
    today = django_timezone.now().date()

    if period_filter == 'today':
        orders = orders.filter(created_at__date=today)
    elif period_filter == 'week':
        week_ago = today - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=week_ago)
    elif period_filter == 'month':
        month_ago = today - timedelta(days=30)
        orders = orders.filter(created_at__date__gte=month_ago)
    elif period_filter == 'year':
        year_ago = today - timedelta(days=365)
        orders = orders.filter(created_at__date__gte=year_ago)

    # Filtre par montant minimum
    min_amount = request.GET.get('min_amount', '')
    if min_amount:
        orders = orders.filter(total_price__gte=float(min_amount))

    # Filtre par recherche
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # === STATISTIQUES (basées sur les filtres appliqués) ===
    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0
    average_order = orders.aggregate(avg=Avg('total_price'))['avg'] or 0

    # Commandes par période (pour les statistiques latérales)
    today_orders = Order.objects.filter(created_at__date=today)
    week_orders = Order.objects.filter(created_at__date__gte=today - timedelta(days=7))
    month_orders = Order.objects.filter(created_at__date__gte=today - timedelta(days=30))

    # Compter les commandes en attente (pour l'affichage)
    pending_orders_count = orders.filter(status='PENDING').count()

    context = {
        'orders': orders,
        'total_revenue': total_revenue,
        'average_order': average_order,
        'today_orders': today_orders,
        'week_orders': week_orders,
        'month_orders': month_orders,
        'pending_orders_count': pending_orders_count,

        # Valeurs actuelles des filtres pour les pré-remplir
        'current_status': status_filter,
        'current_period': period_filter,
        'current_min_amount': min_amount,
        'current_search': search_query,
    }

    return render(request, 'administration/orders.html', context)

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_repairs(request):
    """Vue pour la gestion des réparations"""
    repairs = RepairRequest.objects.all().order_by('-created_at')

    # Statistiques
    pending_repairs = repairs.filter(status='PENDING')
    in_progress_repairs = repairs.filter(status='IN_PROGRESS')
    completed_repairs = repairs.filter(status='COMPLETED')
    screen_repairs = repairs.filter(issue_type='SCREEN')
    battery_repairs = repairs.filter(issue_type='BATTERY')
    charge_repairs = repairs.filter(issue_type='CHARGE')
    water_repairs = repairs.filter(issue_type='WATER')
    other_repairs = repairs.filter(issue_type='OTHER')

    context = {
        'repairs': repairs,
        'pending_repairs': pending_repairs,
        'in_progress_repairs': in_progress_repairs,
        'completed_repairs': completed_repairs,
        'screen_repairs': screen_repairs,
        'battery_repairs': battery_repairs,
        'charge_repairs': charge_repairs,
        'water_repairs': water_repairs,
        'other_repairs': other_repairs,
    }
    return render(request, 'administration/repairs.html', context)


@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_custom_quotes(request):
    """Vue pour la gestion des demandes de devis personnalisé"""
    quotes = CustomQuoteRequest.objects.all().select_related('product').order_by('-created_at')

    # Filtres
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    if status_filter:
        quotes = quotes.filter(status=status_filter.upper())

    if type_filter:
        quotes = quotes.filter(product__decoration_type=type_filter)

    # Statistiques
    pending_quotes = quotes.filter(status='PENDING')
    scheduled_quotes = quotes.filter(status='SCHEDULED')
    completed_quotes = quotes.filter(status='COMPLETED')

    # Répartition par type de produit
    sheet_quotes = quotes.filter(product__decoration_type='SHEET')
    curtain_quotes = quotes.filter(product__decoration_type='CURTAIN')
    carpet_quotes = quotes.filter(product__decoration_type='CARPET')
    other_quotes = quotes.filter(product__decoration_type='OTHER')

    context = {
        'quotes': quotes,
        'pending_quotes': pending_quotes,
        'scheduled_quotes': scheduled_quotes,
        'completed_quotes': completed_quotes,
        'sheet_quotes': sheet_quotes,
        'curtain_quotes': curtain_quotes,
        'carpet_quotes': carpet_quotes,
        'other_quotes': other_quotes,
        'current_status': status_filter,
        'current_type': type_filter,
    }
    return render(request, 'administration/custom_quotes.html', context)

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_repair_detail(request, repair_id):
    """Vue pour les détails d'une réparation"""
    repair = get_object_or_404(RepairRequest, id=repair_id)

    context = {
        'repair': repair,
    }
    return render(request, 'administration/repair_detail.html', context)

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_repair_update_status(request, repair_id):
    """Vue pour mettre à jour le statut d'une réparation"""
    if request.method == 'POST':
        repair = get_object_or_404(RepairRequest, id=repair_id)
        new_status = request.POST.get('status')

        if new_status in dict(RepairRequest.STATUS_CHOICES).keys():
            repair.status = new_status
            repair.save()
            messages.success(request, f"Statut de la réparation #{repair.id} mis à jour !")
        else:
            messages.error(request, "Statut invalide.")

        return redirect('/gestion-securisee/repairs/')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_repair_complete(request, repair_id):
    """Vue pour marquer une réparation comme terminée"""
    if request.method == 'POST':
        repair = get_object_or_404(RepairRequest, id=repair_id)
        repair.status = 'COMPLETED'
        repair.save()
        messages.success(request, f"Réparation #{repair.id} marquée comme terminée !")

        return redirect('/gestion-securisee/repairs/')


@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_repair_delete(request, repair_id):
    """Vue pour supprimer une réparation"""
    if request.method == 'POST':
        repair = get_object_or_404(RepairRequest, id=repair_id)
        repair_id = repair.id
        repair.delete()
        messages.success(request, f"Réparation #{repair_id} supprimée !")

        return redirect('/gestion-securisee/repairs/')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_add_product(request):
    """Vue pour ajouter un produit"""

    if request.method == 'POST':
        # Récupérer les données du formulaire de base
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        product_type = request.POST.get('product_type')  # Soit 'PHONE' soit 'DECORATION'
        stock = request.POST.get('stock')
        discount_percentage = request.POST.get('discount_percentage', 0)
        image = request.FILES.get('image')

        # Gestion des produits de décoration (inclut maintenant les draps)
        needs_custom_quote = request.POST.get('needs_custom_quote') == 'on'
        decoration_type = request.POST.get('decoration_type')  # 'SHEET', 'CURTAIN', etc.
        price_per_sqm = request.POST.get('price_per_sqm')

        # ✅ VALIDATION SIMPLIFIÉE - Plus de distinction SHEET/PHONE/DECORATION
        required_fields = [
            ('name', 'Nom'),
            ('description', 'Description'),
            ('product_type', 'Type de produit'),
            ('stock', 'Stock')
        ]

        # Si pas sur devis, le prix est obligatoire
        if not needs_custom_quote:
            required_fields.append(('price', 'Prix'))

        missing_fields = []
        for field, field_name in required_fields:
            value = request.POST.get(field)
            if not value or not value.strip():
                missing_fields.append(field_name)

        if missing_fields:
            messages.error(request, f"Champs obligatoires manquants: {', '.join(missing_fields)}")
            return redirect('/gestion-securisee/products/add/')

        # Validation de l'image
        if not image:
            messages.error(request, "Veuillez sélectionner une image.")
            return redirect('/gestion-securisee/products/add/')

        # ✅ NOUVELLE VALIDATION UNIFIÉE
        if product_type == 'PHONE':
            phone_brand = request.POST.get('phone_brand')
            if not phone_brand:
                messages.error(request, "Pour les téléphones, la marque est obligatoire.")
                return redirect('/gestion-securisee/products/add/')

        elif product_type == 'DECORATION':
            if not decoration_type:
                messages.error(request, "Pour les produits de décoration, le type est obligatoire.")
                return redirect('/gestion-securisee/products/add/')

            # Validation spécifique pour les draps
            if decoration_type == 'SHEET':
                sheet_size = request.POST.get('sheet_size')
                color = request.POST.get('color')
                if not sheet_size or not color:
                    missing_specs = []
                    if not sheet_size: missing_specs.append("taille")
                    if not color: missing_specs.append("couleur")
                    messages.error(request, f"Pour les draps, les champs suivants sont obligatoires: {', '.join(missing_specs)}")
                    return redirect('/gestion-securisee/products/add/')

        try:
            # ✅ CRÉATION DU PRODUIT AVEC STRUCTURE UNIFIÉE
            product = Product(
                name=name,
                description=description,
                price=price if not needs_custom_quote else 0,  # Prix à 0 si sur devis
                product_type=product_type,
                stock=stock,
                discount_percentage=discount_percentage,
                on_sale=bool(discount_percentage and int(discount_percentage) > 0),
                # Champs pour la décoration (utilisés aussi pour les draps maintenant)
                needs_custom_quote=needs_custom_quote,
                decoration_type=decoration_type if product_type == 'DECORATION' else None,
                price_per_sqm=price_per_sqm if product_type == 'DECORATION' and price_per_sqm else None
            )

            # ✅ GESTION DES SPÉCIFICATIONS PAR TYPE
            if product_type == 'PHONE':
                product.phone_brand = request.POST.get('phone_brand')
                product.phone_category = request.POST.get('phone_category')
                product.storage = request.POST.get('storage')
                product.screen_size = request.POST.get('screen_size')
                product.processor = request.POST.get('processor')
                product.ram = request.POST.get('ram')
                product.camera = request.POST.get('camera')
                product.battery = request.POST.get('battery')
                product.operating_system = request.POST.get('operating_system')
                product.connectivity = request.POST.get('connectivity')

            elif product_type == 'DECORATION':
                # Spécifications pour les draps
                if decoration_type == 'SHEET':
                    product.sheet_size = request.POST.get('sheet_size')
                    product.color = request.POST.get('color')
                    product.material = request.POST.get('material')

            if image:
                product.image = image

            # ✅ SAUVEGARDE (la catégorie sera assignée automatiquement via save())
            product.save()

            messages.success(request, f"Le produit '{name}' a été créé avec succès !")
            return redirect('/gestion-securisee/products/')

        except Exception as e:
            messages.error(request, f"Erreur lors de la création du produit: {str(e)}")
            return redirect('/gestion-securisee/products/add/')

    # GET request - afficher le formulaire
    return render(request, 'administration/add_product.html')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_order_detail(request, order_id):
    """Vue pour les détails d'une commande"""
    # Préfetch les OrderItems avec les produits
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id
    )

    context = {
        'order': order,
        'order_status': order.status,
        'order_status_display': order.get_status_display()
    }
    return render(request, 'administration/order_detail.html', context)

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_order_cancel(request, order_id):
    """Vue pour annuler une commande"""
    if request.method == 'POST':
        order = get_object_or_404(
            Order.objects.prefetch_related('items__product'),
            id=order_id
        )

        # Vérifier si la commande peut être annulée
        if order.status not in ['DELIVERED']:
            # Annuler la commande
            order.status = 'CANCELLED'
            order.save()

            # Remettre les produits en stock via OrderItem
            for item in order.items.all():  # ✅ CORRIGÉ : order.items.all()
                if item.product:  # Vérifier que le produit existe encore
                    item.product.stock += item.quantity
                    item.product.save()

            messages.success(request,
                             f"La commande #{order.order_number} a été annulée et le stock a été réapprovisionné.")
        else:
            messages.error(request, f"Impossible d'annuler une commande déjà livrée.")

        return redirect('/gestion-securisee/orders/')

    return redirect('/gestion-securisee/orders/')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_order_confirm(request, order_id):
    """Vue pour confirmer une commande"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)

        if order.status == 'PENDING':
            order.status = 'CONFIRMED'
            order.save()
            messages.success(request, f"La commande #{order.order_number} a été confirmée avec succès !")
        else:
            messages.warning(request, f"La commande #{order.order_number} a déjà été traitée.")

        return redirect('/gestion-securisee/orders/')

    return redirect('/gestion-securisee/orders/')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_order_update_status(request, order_id):
    """Vue pour mettre à jour le statut d'une commande"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES).keys():
            # Si on annule une commande, remettre les produits en stock
            if new_status == 'CANCELLED' and order.status != 'CANCELLED':
                # Précharger les items pour la mise à jour du stock
                order = get_object_or_404(
                    Order.objects.prefetch_related('items__product'),
                    id=order_id
                )
                for item in order.items.all():
                    if item.product:
                        item.product.stock += item.quantity
                        item.product.save()

            order.status = new_status
            order.save()
            messages.success(request, f"Statut de la commande #{order.order_number} mis à jour !")
        else:
            messages.error(request, "Statut invalide.")

        return redirect(f'/gestion-securisee/orders/{order_id}/')

    return redirect('/gestion-securisee/orders/')

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_order_export(request, order_id):
    """Vue pour exporter une commande en PDF avec reportlab"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.lib import colors
    from django.utils import timezone

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id
    )

    try:
        # Créer la réponse HTTP
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="commande_{order.order_number}.pdf"'

        # Créer le document PDF
        doc = SimpleDocTemplate(response, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
        elements = []
        styles = getSampleStyleSheet()

        # === EN-TÊTE ===
        elements.append(Paragraph("FACTURE", styles['Heading1']))
        elements.append(Paragraph(f"Commande #{order.order_number}", styles['Heading2']))
        elements.append(Spacer(1, 15))

        # === INFORMATIONS SOCIÉTÉ ET DATE ===
        company_data = [
            ["Tech & Home", f"Date: {order.created_at.strftime('%d/%m/%Y')}"],
            ["Abidjan, Côte d'Ivoire", f"Heure: {order.created_at.strftime('%H:%M')}"],
            ["Tél: +225 07 07 07 07 07", f"Statut: {order.get_status_display()}"],
            ["Email: contact@techandhome.ci", f"Ref: {order.order_number}"],
        ]

        company_table = Table(company_data, colWidths=[100 * mm, 90 * mm])
        company_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 20))

        # === INFORMATIONS CLIENT ===
        elements.append(Paragraph("INFORMATIONS CLIENT", styles['Heading3']))
        client_data = [
            ["Nom complet:", order.full_name],
            ["Email:", order.email],
            ["Téléphone:", order.phone_number],
            ["Adresse:", f"{order.address}"],
            ["Ville:", f"{order.city}, {order.country}"],
        ]

        client_table = Table(client_data, colWidths=[30 * mm, 160 * mm])
        client_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(client_table)
        elements.append(Spacer(1, 20))

        # === ARTICLES COMMANDÉS ===
        elements.append(Paragraph("ARTICLES COMMANDÉS", styles['Heading3']))

        # Préparer les données du tableau
        items_data = [["Qté", "Description", "Prix unit.", "Total"]]

        for item in order.items.all():
            # Description du produit
            description = item.product_name
            if item.product:
                if item.product.product_type == 'SHEET':
                    description += f" - {item.product.get_sheet_size_display()} - {item.product.get_color_display()}"
                    if item.product.material:
                        description += f" ({item.product.material})"
                elif item.product.product_type == 'PHONE':
                    description += f" - {item.product.get_phone_brand_display()}"
                    if item.product.storage:
                        description += f" - {item.product.storage}"

            items_data.append([
                str(item.quantity),
                description,
                f"{item.product_price:.2f} €",
                f"{item.get_total_price():.2f} €"
            ])

        # Créer le tableau des articles
        items_table = Table(items_data, colWidths=[15 * mm, 110 * mm, 30 * mm, 25 * mm])
        items_table.setStyle(TableStyle([
            # En-tête
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Données
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Quantité centrée
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),  # Prix alignés à droite
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # Bordures
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#adb5bd')),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 20))

        # === TOTAL ===
        total_data = [
            ["", ""],
            ["Sous-total:", f"{order.total_price:.2f} €"],
            ["Livraison:", "Gratuite"],
            ["", ""],
            ["TOTAL:", f"{order.total_price:.2f} €"],
        ]

        total_table = Table(total_data, colWidths=[120 * mm, 60 * mm])
        total_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 4), (-1, 4), 'Helvetica-Bold', 12),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 4), (-1, 4), 1, colors.black),
            ('TOPPADDING', (4, 0), (4, -1), 10),
            ('BOTTOMPADDING', (4, 0), (4, -1), 10),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 30))

        # === INFORMATIONS SUPPLÉMENTAIRES ===
        elements.append(Paragraph("INFORMATIONS SUPPLÉMENTAIRES", styles['Heading3']))
        info_text = f"""
        <para>
        <b>Numéro de commande:</b> {order.order_number}<br/>
        <b>Date de création:</b> {order.created_at.strftime('%d/%m/%Y à %H:%M')}<br/>
        <b>Dernière modification:</b> {order.updated_at.strftime('%d/%m/%Y à %H:%M')}<br/>
        <b>Document généré le:</b> {timezone.now().strftime('%d/%m/%Y à %H:%M')}
        </para>
        """
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # === PIED DE PAGE ===
        footer_text = """
        <para alignment="center">
        <font size="8" color="gray">
        DSD General Trading - Abidjan, Côte d'Ivoire<br/>
        Tél: +225 07 07 07 07 07 - Email: contact@techandhome.ci<br/>
        Ce document a une valeur informative et constitue une preuve d'achat.
        </font>
        </para>
        """
        elements.append(Paragraph(footer_text, styles['Normal']))

        # === GÉNÉRER LE PDF ===
        doc.build(elements)
        return response

    except Exception as e:
        # En cas d'erreur, utiliser l'export HTML en fallback
        return export_html_fallback(request, order)

@admin_required
def export_html_fallback(request, order):
    """Fallback HTML si le PDF échoue"""
    from django.utils import timezone

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Facture - Commande {order.order_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
            .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
            .invoice-title {{ font-size: 24px; font-weight: bold; }}
            .invoice-number {{ font-size: 18px; color: #666; }}
            .section {{ margin-bottom: 25px; }}
            .section-title {{ font-size: 16px; font-weight: bold; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            .text-right {{ text-align: right; }}
            .text-center {{ text-align: center; }}
            .total-section {{ margin-top: 30px; text-align: right; font-size: 14px; }}
            .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="invoice-title">FACTURE</div>
            <div class="invoice-number">Commande #{order.order_number}</div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 30px;">
            <div>
                <strong>Tech & Home</strong><br>
                Abidjan, Côte d'Ivoire<br>
                Tél: +225 07 07 07 07 07<br>
                Email: contact@techandhome.ci
            </div>
            <div style="text-align: right;">
                <strong>Date:</strong> {order.created_at.strftime('%d/%m/%Y')}<br>
                <strong>Heure:</strong> {order.created_at.strftime('%H:%M')}<br>
                <strong>Statut:</strong> {order.get_status_display()}<br>
                <strong>Réf:</strong> {order.order_number}
            </div>
        </div>

        <div class="section">
            <div class="section-title">INFORMATIONS CLIENT</div>
            <strong>Nom complet:</strong> {order.full_name}<br>
            <strong>Email:</strong> {order.email}<br>
            <strong>Téléphone:</strong> {order.phone_number}<br>
            <strong>Adresse:</strong> {order.address}, {order.city}, {order.country}
        </div>

        <div class="section">
            <div class="section-title">ARTICLES COMMANDÉS</div>
            <table>
                <thead>
                    <tr>
                        <th>Qté</th>
                        <th>Description</th>
                        <th>Prix unitaire</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Ajouter les articles
    for item in order.items.all():
        description = item.product_name
        if item.product:
            if item.product.product_type == 'SHEET':
                description += f" - {item.product.get_sheet_size_display()} - {item.product.get_color_display()}"
            elif item.product.product_type == 'PHONE':
                description += f" - {item.product.get_phone_brand_display()}"

        html_content += f"""
                    <tr>
                        <td class="text-center">{item.quantity}</td>
                        <td>{description}</td>
                        <td class="text-right">{item.product_price:.2f} €</td>
                        <td class="text-right">{item.get_total_price():.2f} €</td>
                    </tr>
        """

    html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="total-section">
            <strong>Sous-total: {order.total_price:.2f} €</strong><br>
            <strong>Livraison: Gratuite</strong><br>
            <strong style="font-size: 16px;">TOTAL: {order.total_price:.2f} €</strong>
        </div>

        <div class="footer">
            Document généré le {timezone.now().strftime('%d/%m/%Y à %H:%M')} - Tech & Home<br>
            Ce document a une valeur informative et constitue une preuve d'achat.
        </div>
    </body>
    </html>
    """

    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="commande_{order.order_number}.html"'
    return response

@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_edit_product(request, product_id):
    """Vue pour modifier un produit existant"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            product_type = request.POST.get('product_type')
            discount_percentage = request.POST.get('discount_percentage', 0)
            image = request.FILES.get('image')

            # NOUVEAU : Gestion des produits de décoration
            needs_custom_quote = request.POST.get('needs_custom_quote') == 'on'
            decoration_type = request.POST.get('decoration_type')
            price_per_sqm = request.POST.get('price_per_sqm')

            # Mettre à jour les champs de base
            product.name = name
            product.description = description
            product.price = price if not needs_custom_quote else 0
            product.stock = stock
            product.product_type = product_type
            product.discount_percentage = discount_percentage
            product.on_sale = bool(discount_percentage and int(discount_percentage) > 0)
            # NOUVEAUX CHAMPS
            product.needs_custom_quote = needs_custom_quote
            product.decoration_type = decoration_type if product_type == 'DECORATION' else None
            product.price_per_sqm = price_per_sqm if product_type == 'DECORATION' and price_per_sqm else None

            # Mettre à jour l'image si une nouvelle est fournie
            if image:
                product.image = image

            # Mettre à jour les spécifications selon le type
            if product_type == 'SHEET':
                product.sheet_size = request.POST.get('sheet_size')
                product.color = request.POST.get('color')
                product.material = request.POST.get('material')

                # Réinitialiser les champs téléphone et décoration
                product.phone_brand = None
                product.phone_category = None
                product.storage = ''
                product.screen_size = ''
                product.processor = ''
                product.ram = ''
                product.camera = ''
                product.battery = ''
                product.operating_system = ''
                product.connectivity = ''

            elif product_type == 'PHONE':
                product.phone_brand = request.POST.get('phone_brand')
                product.phone_category = request.POST.get('phone_category')
                product.storage = request.POST.get('storage')
                product.screen_size = request.POST.get('screen_size')
                product.processor = request.POST.get('processor')
                product.ram = request.POST.get('ram')
                product.camera = request.POST.get('camera')
                product.battery = request.POST.get('battery')
                product.operating_system = request.POST.get('operating_system')
                product.connectivity = request.POST.get('connectivity')

                # Réinitialiser les champs draps et décoration
                product.sheet_size = None
                product.color = None
                product.material = ''

            elif product_type == 'DECORATION':
                # Réinitialiser les champs spécifiques aux autres types
                product.sheet_size = None
                product.color = None
                product.material = ''
                product.phone_brand = None
                product.phone_category = None
                product.storage = ''
                product.screen_size = ''
                product.processor = ''
                product.ram = ''
                product.camera = ''
                product.battery = ''
                product.operating_system = ''
                product.connectivity = ''

            # Sauvegarder les modifications
            product.save()

            messages.success(request, f"Le produit '{product.name}' a été modifié avec succès !")
            return redirect('/gestion-securisee/products/')

        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")

    # Préparer les données pour le template
    context = {
        'product': product,
        'categories': Category.objects.all(),
    }

    return render(request, 'administration/edit_product.html', context)


@admin_required
@login_required
@user_passes_test(is_admin_user)
def admin_edit_quote(request, quote_id):
    """Vue pour modifier une demande de devis"""
    quote = get_object_or_404(CustomQuoteRequest, id=quote_id)

    if request.method == 'POST':
        # Traiter la modification
        quote.status = request.POST.get('status')
        quote.admin_notes = request.POST.get('admin_notes', '')
        quoted_price = request.POST.get('quoted_price')
        if quoted_price:
            quote.quoted_price = quoted_price
        quote.save()

        messages.success(request, "Devis mis à jour avec succès !")
        return redirect('shop:admin_custom_quotes')

    context = {
        'quote': quote,
        'status_choices': CustomQuoteRequest.STATUS_CHOICES
    }
    return render(request, 'administration/edit_quote.html', context)