# utils/emails.py - VERSION SECOURS
import logging

logger = logging.getLogger(__name__)

def send_new_order_notification(order):
    """Version secours - juste logger, pas d'email"""
    try:
        logger.info(f"📦 NOUVELLE COMMANDE #{order.order_number}")
        logger.info(f"Client: {order.full_name} - {order.email}")
        logger.info(f"Montant: {order.total_price} FCFA")
        logger.info("🔔 Notification enregistrée (emails désactivés)")
        return True
    except Exception as e:
        logger.error(f"Erreur notification commande: {e}")
        return True  # ⚠️ TOUJOURS retourner True pour ne pas bloquer

def send_quote_request_notification(quote_request):
    """Version secours - juste logger"""
    try:
        logger.info(f"📋 DEMANDE DEVIS - {quote_request.product.name}")
        logger.info(f"Client: {quote_request.full_name} - {quote_request.email}")
        logger.info("🔔 Notification enregistrée (emails désactivés)")
        return True
    except Exception as e:
        logger.error(f"Erreur notification devis: {e}")
        return True

def send_repair_request_notification(repair_request):
    """Version secours - juste logger"""
    try:
        logger.info(f"🔧 DEMANDE RÉPARATION - {repair_request.device_model}")
        logger.info(f"Client: {repair_request.full_name} - {repair_request.email}")
        logger.info("🔔 Notification enregistrée (emails désactivés)")
        return True
    except Exception as e:
        logger.error(f"Erreur notification réparation: {e}")
        return True