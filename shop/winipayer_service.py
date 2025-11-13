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

    # shop/winipayer_service.py - MODIFIEZ create_payment

    def create_payment(self, order, return_url, cancel_url, callback_url):
        """
        Créer un paiement Winipayer EXPRESS avec les URLs de retour
        """
        try:
            print("=" * 60)
            print("🔄 DÉBUT CRÉATION PAIEMENT WINIPAYER")
            print("=" * 60)

            print(f"🔧 Configuration Winipayer:")
            print(f"  - UUID: {self.merchant_uuid}")
            print(f"  - Environnement: {self.env}")
            print(f"  - Montant: {order.total_price}")
            print(f"  - Order ID: {order.id}")
            print(f"  - Return URL: {return_url}")
            print(f"  - Cancel URL: {cancel_url}")
            print(f"  - Callback URL: {callback_url}")

            # Préparer les headers
            headers = {
                'X-Merchant-uuid': self.merchant_uuid,
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            # ⭐ PAYLOAD COMPLET avec toutes les URLs
            payload = {
                "env": self.env,
                "amount": int(float(order.total_price)),
                "client_pay_fee": "false",
                "metadata": json.dumps({"order_id": str(order.id)}),  # Format JSON correct
                "return_url": return_url,  # Où rediriger après succès
                "cancel_url": cancel_url,  # Où rediriger après annulation
                "callback_url": callback_url,  # Où envoyer le webhook
                "currency": "XOF",  # Devise
                "description": f"Commande #{order.order_number}",
            }

            print(f"🔍 Payload COMPLET envoyé à Winipayer:")
            for key, value in payload.items():
                print(f"  {key}: {value}")

            # URL de l'API Winipayer
            api_url = f"{self.base_url}/checkout/express/create"
            print(f"🌐 URL API: {api_url}")

            # Faire la requête
            print("🔄 Envoi de la requête à Winipayer...")
            response = requests.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=30
            )

            print("=" * 60)
            print("📡 RÉPONSE DE WINIPAYER")
            print("=" * 60)
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            print(f"  Contenu: {response.text}")

            # Traiter la réponse
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📊 Données JSON parsées: {data}")

                    if data.get('success'):
                        results = data['results']
                        print("🎉 PAIEMENT CRÉÉ AVEC SUCCÈS!")
                        print(f"   - UUID: {results.get('uuid')}")
                        print(f"   - URL Paiement: {results.get('checkout_process')}")
                        print(f"   - Crypto: {results.get('crypto')}")
                        print(f"   - Expire le: {results.get('expired_at')}")

                        return {
                            'success': True,
                            'payment_url': results.get('checkout_process'),
                            'transaction_id': results.get('uuid'),
                            'crypto': results.get('crypto'),
                            'expired_at': results.get('expired_at'),
                            'raw_response': data
                        }
                    else:
                        error_data = data.get('errors', {})
                        error_msg = error_data.get('msg', 'Erreur inconnue de Winipayer')
                        error_code = error_data.get('code', 'N/A')

                        print(f"❌ ERREUR WINIPAYER:")
                        print(f"   - Code: {error_code}")
                        print(f"   - Message: {error_msg}")
                        print(f"   - Données complètes: {error_data}")

                        return {
                            'success': False,
                            'error': f"Winipayer [{error_code}]: {error_msg}",
                            'error_details': error_data
                        }

                except json.JSONDecodeError as e:
                    print(f"❌ ERREUR: Impossible de parser la réponse JSON")
                    print(f"   - Réponse brute: {response.text}")
                    return {
                        'success': False,
                        'error': f"Erreur de format JSON: {str(e)}"
                    }

            elif response.status_code == 400:
                print("❌ ERREUR 400: Requête mal formée")
                return {
                    'success': False,
                    'error': "Requête mal formée (400). Vérifiez les paramètres."
                }
            elif response.status_code == 401:
                print("❌ ERREUR 401: Non autorisé")
                return {
                    'success': False,
                    'error': "Clé API ou UUID incorrect (401)"
                }
            elif response.status_code == 500:
                print("❌ ERREUR 500: Problème serveur Winipayer")
                return {
                    'success': False,
                    'error': "Problème serveur Winipayer (500)"
                }
            else:
                print(f"❌ ERREUR HTTP: {response.status_code}")
                return {
                    'success': False,
                    'error': f"Erreur HTTP {response.status_code}: {response.text}"
                }

        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: La requête a expiré")
            return {
                'success': False,
                'error': "Timeout: La requête a pris trop de temps"
            }
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Impossible de se connecter à Winipayer")
            return {
                'success': False,
                'error': "Erreur de connexion: Impossible d'atteindre Winipayer"
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST EXCEPTION: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur de requête: {str(e)}"
            }
        except Exception as e:
            print(f"❌ ERREUR INATTENDUE: {str(e)}")
            import traceback
            print(f"Stack trace: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Erreur inattendue: {str(e)}"
            }
        finally:
            print("=" * 60)
            print("🏁 FIN CRÉATION PAIEMENT")
            print("=" * 60)

    def check_payment_status(self, transaction_crypto):
        """
        Vérifier le statut d'un paiement Express
        """
        try:
            print(f"🔍 Vérification statut paiement: {transaction_crypto}")

            headers = {
                'X-Merchant-uuid': self.merchant_uuid,
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            payload = {
                "env": self.env
            }

            response = requests.post(
                f"{self.base_url}/checkout/express/detail/{transaction_crypto}",
                data=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"📊 Statut paiement: {data}")
                return data
            else:
                print(f"❌ Erreur vérification statut: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Erreur vérification paiement: {str(e)}")
            return None