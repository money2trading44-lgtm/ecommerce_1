from django.core.mail import send_mail
from django.conf import settings


def send_new_order_notification(order):
    """Envoie une notification pour nouvelle commande"""
    subject = f"🛒 Nouvelle commande #{order.order_number}"

    products_list = "\n".join([f"- {item.product_name} x {item.quantity}" for item in order.items.all()])

    message = f"""
Nouvelle commande reçue sur DSD Trading !

📋 DÉTAILS DE LA COMMANDE:
Numéro: #{order.order_number}
Montant: {order.total_price} FCFA
Méthode de paiement: {order.get_payment_method_display()}
Statut: {order.get_payment_status_display()}

👤 INFORMATIONS CLIENT:
Nom: {order.full_name}
Email: {order.email}
Téléphone: {order.phone_number}
Adresse: {order.address}, {order.city}

📦 PRODUITS COMMANDÉS:
{products_list}

Consultez la commande dans l'administration.
"""

    send_mail(
        subject,
        message.strip(),
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )


def send_quote_request_notification(quote_request):
    """Envoie une notification pour demande de devis"""
    subject = f"📋 Demande de devis - {quote_request.product.name}"
    message = f"""
Nouvelle demande de devis !

👤 CLIENT:
Nom: {quote_request.full_name}
Email: {quote_request.email}
Téléphone: {quote_request.phone_number}
Adresse: {quote_request.address}, {quote_request.city}

📦 PRODUIT:
{quote_request.product.name}

📅 RENDEZ-VOUS SOUHAITÉ:
Date: {quote_request.preferred_date}
Heure: {quote_request.preferred_time}

📏 MESURES:
Dimensions pièce: {quote_request.room_dimensions or 'Non précisé'}
Mesures fenêtres: {quote_request.window_measurements or 'Non précisé'}
Taille lit: {quote_request.bed_size or 'Non précisé'}

🎨 PRÉFÉRENCES:
Tissu: {quote_request.fabric_preference or 'Non précisé'}
Couleurs: {quote_request.color_preferences or 'Non précisé'}

💬 DEMANDES SPÉCIALES:
{quote_request.special_requests or 'Aucune'}

Contactez le client rapidement.
"""

    send_mail(
        subject,
        message.strip(),
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )


def send_repair_request_notification(repair_request):
    """Envoie une notification pour demande de réparation"""
    subject = f"🔧 Demande de réparation - {repair_request.device_model}"
    message = f"""
Nouvelle demande de réparation !

👤 CLIENT:
Nom: {repair_request.full_name}
Email: {repair_request.email}
Téléphone: {repair_request.phone_number}

📱 APPAREIL:
Modèle: {repair_request.device_model}
Type de problème: {repair_request.issue_type}

🔧 DESCRIPTION DU PROBLÈME:
{repair_request.description}

Contactez le client rapidement.
"""

    send_mail(
        subject,
        message.strip(),
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )