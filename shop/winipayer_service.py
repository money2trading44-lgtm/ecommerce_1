import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WinipayerService:
    def __init__(self):
        self.merchant_uuid = "ae3792f7-67ba-4cca-b878-37694a7d3136"  # ⭐ REMPLACE PAR TON UUID
        self.private_key = settings.WINIPAYER_API_KEY
        self.base_url = "https://api-v2.winipayer.com"
        self.env = 'prod'

    def create_payment(self, order, return_url, cancel_url, callback_url):
        """
        Créer un paiement Winipayer EXPRESS (API simplifiée)
        """
        try:
            print(f"🔧 API Express Winipayer - Mode: {self.env}")

            # ⭐ HEADERS SIMPLIFIÉS POUR L'API EXPRESS
            headers = {
                'X-Merchant-uuid': self.merchant_uuid,  # ⭐ UUID au lieu de Apply/Token
            }

            # ⭐ PAYLOAD SIMPLIFIÉ POUR L'API EXPRESS
            payload = {
                "env": self.env,
                "amount": int(float(order.total_price)),
                "client_pay_fee": "false",  # Le marchand paye les frais
            }

            # ⭐ LOGS COMPLETS
            print("=" * 60)
            print("🔍 PAYLOAD EXPRESS ENVOYÉ À WINIPAYER:")
            print(f"  env: '{payload['env']}'")
            print(f"  amount: {payload['amount']}")
            print(f"  client_pay_fee: '{payload['client_pay_fee']}'")
            print(f"  Headers: {headers}")
            print("=" * 60)

            # ⭐ ENDPOINT EXPRESS
            api_url = f"{self.base_url}/checkout/express/create"
            print(f"🌐 URL API Express: {api_url}")

            response = requests.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=30,
                #verify=False
            )

            # ⭐ LOGS DE LA RÉPONSE
            print("=" * 60)
            print("📡 RÉPONSE EXPRESS WINIPAYER:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Content: {response.text}")
            print("=" * 60)

            if response.status_code == 200:
                data = response.json()
                print(f"📊 Données JSON parsées: {data}")

                if data.get('success'):
                    results = data['results']

                    print(f"🎉 SUCCÈS API Express!")
                    print(f"  UUID: {results['uuid']}")
                    print(f"  Crypto: {results['crypto'][:30]}...")
                    print(f"  URL Paiement: {results['checkout_process']}")

                    return {
                        'success': True,
                        'payment_url': results['checkout_process'],
                        'transaction_id': results['uuid'],
                        'crypto': results['crypto'],
                        'expired_at': results['expired_at']
                    }
                else:
                    error_data = data.get('errors', {})
                    error_msg = error_data.get('msg', 'Erreur inconnue de Winipayer')
                    error_code = error_data.get('code', 'N/A')

                    print(f"❌ Erreur API Express - Code: {error_code}, Message: {error_msg}")
                    print(f"❌ Données d'erreur: {error_data}")

                    return {
                        'success': False,
                        'error': f"Winipayer Express [{error_code}]: {error_msg}"
                    }
            else:
                print(f"❌ Erreur HTTP: {response.status_code}")
                return {
                    'success': False,
                    'error': f"Erreur HTTP {response.status_code}"
                }

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur de réseau: {str(e)}"
            }
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur technique: {str(e)}"
            }

    def check_payment_status(self, transaction_crypto):
        """
        Vérifier le statut d'un paiement Express
        """
        try:
            headers = {
                'X-Merchant-uuid': self.merchant_uuid,
            }

            payload = {
                "env": self.env
            }

            response = requests.post(
                f"{self.base_url}/checkout/express/detail/{transaction_crypto}",
                data=payload,
                headers=headers,
                timeout=30,
                verify=False
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erreur vérification statut: {response.status_code}")
                return None

        except Exception as e:
            print(f"Erreur vérification paiement: {str(e)}")
            return None