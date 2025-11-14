import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WinipayerService:
    def __init__(self):
        self.merchant_apply = settings.WINIPAYER_MERCHANT_APPLY_KEY
        self.api_key = settings.WINIPAYER_API_KEY
        self.base_url = "https://api-v2.winipayer.com"
        self.env = "prod"

    def create_payment(self, order, return_url, cancel_url, callback_url):
        """
        Créer un paiement Winipayer STANDARD - Format exact cURL
        """
        try:
            print("=" * 60)
            print("🔄 API STANDARD - FORMAT CURL")
            print("=" * 60)

            print(f"🔧 Configuration:")
            print(f"  - Apply: {self.merchant_apply}")
            print(f"  - Token: {self.api_key}")
            print(f"  - Env: {self.env}")

            # Headers exacts comme cURL
            headers = {
                'X-Merchant-Apply': self.merchant_apply,
                'X-Merchant-Token': self.api_key,
            }

            # ⭐ FORMAT EXACT COMME LA DOC CURL - tous les champs en strings
            payload = {
                "env": self.env,
                'amount': int(float(order.total_price)),
                'description': f'Commande #{order.order_number}',
                'client_pay_fee': 'false',
                'cancel_url': f'{cancel_url}',
                'return_url': f'{return_url}',
                'callback_url': f'{callback_url}',
            }

            # ⭐ AJOUTER items SI DISPONIBLE
            items_data = []
            for item in order.items.all():
                items_data.append({
                    "name": item.product_name,
                    "quantity": item.quantity,
                    "price_unit": float(item.product_price),
                    "description": f"Commande #{order.order_number}",
                    "price_total": float(item.get_total_price())
                })

            if items_data:
                payload['items'] = json.dumps(items_data)

            # ⭐ AJOUTER custom_data
            payload['custom_data'] = json.dumps({
                "order_id": str(order.id),
                "order_number": order.order_number
            })

            print(f"🔍 Payload FINAL:")
            for key, value in payload.items():
                print(f"  {key}: {value}")

            api_url = f"{self.base_url}/checkout/standard/create"
            print(f"🌐 URL: {api_url}")

            # ⭐ REQUÊTE AVEC VERIFICATION
            response = requests.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=30
            )

            print("=" * 60)
            print("📡 RÉPONSE COMPLÈTE:")
            print(f"  Status: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            print(f"  Contenu: {response.text}")
            print("=" * 60)

            if response.status_code == 200:
                data = response.json()
                print(f"📊 JSON: {data}")

                if data.get('success'):
                    results = data['results']
                    print("🎉 SUCCÈS API STANDARD !")
                    return {
                        'success': True,
                        'payment_url': results.get('checkout_process'),
                        'transaction_id': results.get('uuid'),
                    }
                else:
                    error_data = data.get('errors', {})
                    error_msg = error_data.get('msg', 'Erreur inconnue')
                    error_code = error_data.get('code', 'N/A')
                    print(f"❌ Erreur détaillée: {error_data}")
                    return {
                        'success': False,
                        'error': f"[{error_code}] {error_msg}",
                        'details': error_data
                    }
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return {
                    'success': False,
                    'error': f"Erreur HTTP {response.status_code}",
                    'response_text': response.text
                }

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback
            print(f"Stack: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Exception: {str(e)}"
            }

    def check_payment_status(self, transaction_uuid):
        """
        Vérifier le statut d'un paiement Standard
        """
        try:
            print(f"🔍 Vérification statut: {transaction_uuid}")

            headers = {
                'X-Merchant-Apply': self.merchant_apply,
                'X-Merchant-Token': self.api_key,
            }

            payload = {
                "env": self.env
            }

            response = requests.post(
                f"{self.base_url}/checkout/standard/detail/{transaction_uuid}",
                data=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"📊 Statut: {data}")
                return data
            else:
                print(f"❌ Erreur vérification: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erreur vérification: {str(e)}")
            return None